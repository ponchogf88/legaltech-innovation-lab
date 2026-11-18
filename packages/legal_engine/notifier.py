"""High-signal alert and email notification engine for LegalTech HITL gates and node handoffs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
import json
import os
from pathlib import Path
import smtplib
from typing import Any

from .security import assert_synthetic_and_safe

ALERT_LEVELS: tuple[str, ...] = (
    "INFO",
    "ACTION_REQUIRED",
    "URGENT_REVIEW",
    "SECURITY_BLOCK",
)


class NotificationError(ValueError):
    """Raised when an alert payload violates schema or synthetic safety guardrails."""


@dataclass(frozen=True)
class AlertNotification:
    """Structured notification payload emitted on critical HITL gates or multi-node handoffs."""

    event_id: str
    timestamp_utc: str
    alert_level: str
    title: str
    summary: str
    matter_id: str
    requires_human_action: bool
    recommended_action: str
    node_origin: str = "MAC_COMMAND_CENTER"

    def to_dict(self) -> dict[str, Any]:
        """Serialize alert notification into a JSON-compatible dict."""
        return asdict(self)


def build_alert_notification(
    *,
    alert_level: str,
    title: str,
    summary: str,
    matter_id: str = "SYSTEM-ORCHESTRATION",
    requires_human_action: bool = True,
    recommended_action: str = "Revisar Command Center y confirmar compuerta HITL.",
    node_origin: str = "MAC_COMMAND_CENTER",
    now: datetime | None = None,
) -> AlertNotification:
    """Construct and validate a PII-safe AlertNotification."""
    if alert_level not in ALERT_LEVELS:
        raise NotificationError(f"Invalid alert_level {alert_level!r}; allowed: {ALERT_LEVELS}")
    if not title.strip() or not summary.strip():
        raise NotificationError("Alert title and summary must be non-empty.")

    assert_synthetic_and_safe({
        "title": title,
        "summary": summary,
        "matter_id": matter_id,
        "recommended_action": recommended_action,
        "node_origin": node_origin,
    })

    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return AlertNotification(
        event_id=f"ALT-{now_utc.strftime('%Y%m%dT%H%M%SZ')}",
        timestamp_utc=now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        alert_level=alert_level,
        title=title.strip(),
        summary=summary.strip(),
        matter_id=matter_id.strip(),
        requires_human_action=requires_human_action,
        recommended_action=recommended_action.strip(),
        node_origin=node_origin.strip(),
    )


def format_alert_email_body(alert: AlertNotification) -> str:
    """Render plain-text body for optional SMTP alert emails."""
    flag = "SÍ (Atención/Revisión requerida)" if alert.requires_human_action else "No (Informativo)"
    return (
        f"[LegalTech Innovation Lab · {alert.alert_level}]\n"
        f"ID: {alert.event_id}\n"
        f"Origen: {alert.node_origin}\n"
        f"Fecha UTC: {alert.timestamp_utc}\n"
        f"Asunto / Expediente: {alert.matter_id}\n"
        f"Requiere acción humana: {flag}\n\n"
        f"Resumen:\n{alert.summary}\n\n"
        f"Siguiente acción recomendada:\n{alert.recommended_action}\n"
    )


def dispatch_alert(
    alert: AlertNotification,
    *,
    log_path: Path | None = None,
    smtp_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append alert to local JSONL queue and optionally deliver over configured SMTP.

    If SMTP configuration is absent or dry_run is enabled, records cleanly to the local
    JSONL alert log without failing offline workflows.
    """
    assert_synthetic_and_safe(alert.to_dict())

    target_log = Path(log_path) if log_path is not None else Path("logs") / "notifications.jsonl"
    target_log.parent.mkdir(parents=True, exist_ok=True)
    with target_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(alert.to_dict(), ensure_ascii=False) + "\n")

    cfg = smtp_config if smtp_config is not None else {}
    host = str(cfg.get("host") or os.environ.get("LEGAL_LAB_SMTP_HOST", "")).strip()
    to_addr = str(cfg.get("to_addr") or os.environ.get("LEGAL_LAB_ALERT_TO", "")).strip()
    from_addr = str(
        cfg.get("from_addr") or os.environ.get("LEGAL_LAB_ALERT_FROM", "noreply@example.invalid")
    ).strip()
    username = str(cfg.get("username") or os.environ.get("LEGAL_LAB_SMTP_USER", "")).strip()
    password = str(cfg.get("password") or os.environ.get("LEGAL_LAB_SMTP_PASSWORD", "")).strip()
    port = int(cfg.get("port") or os.environ.get("LEGAL_LAB_SMTP_PORT", "587"))
    dry_run = bool(cfg.get("dry_run", False))

    if not host or not to_addr or dry_run:
        return {
            "event_id": alert.event_id,
            "status": "LOGGED_LOCAL_QUEUE",
            "log_path": str(target_log),
            "smtp_sent": False,
            "reason": "Dry-run enabled or SMTP host/recipient not configured.",
        }

    msg = EmailMessage()
    msg["Subject"] = f"[LegalTech Lab · {alert.alert_level}] {alert.title}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(format_alert_email_body(alert))

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)

    return {
        "event_id": alert.event_id,
        "status": "SENT_SMTP_AND_LOGGED",
        "log_path": str(target_log),
        "smtp_sent": True,
        "recipient": to_addr,
    }
