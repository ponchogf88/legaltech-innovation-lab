"""Tests for multi-node orchestration handoffs and PII-safe alert notifications."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import pytest

from legal_engine.cli import main as cli_main
from legal_engine.continuity import init_72h_clock, write_node_handshake
from legal_engine.notifier import (
    NotificationError,
    build_alert_notification,
    dispatch_alert,
    format_alert_email_body,
)
from legal_engine.security import SecurityViolationError


def _init_temp_git(repo_dir: Path) -> None:
    subprocess.run(["git", "init", "-b", "dev/mission-002"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo_dir, check=True)
    (repo_dir / "README.md").write_text("# Test Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, check=True, capture_output=True)


def test_build_and_dispatch_alert_notification_logs_cleanly(tmp_path: Path) -> None:
    alert = build_alert_notification(
        alert_level="URGENT_REVIEW",
        title="Última revisión HITL requerida",
        summary="El nodo Dell completó rutina M2-03; requiere aprobación humana antes de emitir.",
        matter_id="EXP-SINT-2026-001",
        requires_human_action=True,
        recommended_action="Abrir Command Center y aprobar compuerta Nomos.",
        node_origin="DELL_WINDOWS_LAB",
        now=datetime(2026, 11, 18, 14, 15, 0, tzinfo=timezone.utc),
    )

    body = format_alert_email_body(alert)
    assert "URGENT_REVIEW" in body
    assert "DELL_WINDOWS_LAB" in body

    log_file = tmp_path / "logs" / "notifications.jsonl"
    result = dispatch_alert(alert, log_path=log_file, smtp_config={"dry_run": True})
    assert result["status"] == "LOGGED_LOCAL_QUEUE"
    assert result["smtp_sent"] is False
    assert log_file.is_file()
    recorded = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert recorded["alert_level"] == "URGENT_REVIEW"
    assert recorded["requires_human_action"] is True


def test_alert_notification_blocks_pii_and_invalid_level() -> None:
    blocked_rfc = "GODE" + "561231" + "GR8"
    with pytest.raises(SecurityViolationError, match="RFC_PATTERN"):
        build_alert_notification(
            alert_level="ACTION_REQUIRED",
            title="Revisión",
            summary=f"Cliente con identificador {blocked_rfc}",
        )

    with pytest.raises(NotificationError, match="Invalid alert_level"):
        build_alert_notification(alert_level="UNKNOWN", title="Hola", summary="Contenido")


def test_write_node_handshake_and_cli_handoff_and_notify(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _init_temp_git(tmp_path)
    init_72h_clock(tmp_path / "72H_CLOCK.json")

    first = write_node_handshake(
        tmp_path,
        from_node="MAC_COMMAND_CENTER",
        to_node="DELL_WINDOWS_LAB",
        instruction_note="Ejecutar ROUTINE-DELL-01 en ramas limpias.",
        ping_id="PING-MAC-TO-DELL-001",
        routines=[{"routine_id": "ROUTINE-DELL-01", "task_id": "M2-03", "status": "READY"}],
        requires_owner_review=True,
    )
    assert first["sequence_number"] == 1
    assert first["next_assigned_node"] == "DELL_WINDOWS_LAB"
    assert first["active_ping_id"] == "PING-MAC-TO-DELL-001"
    assert "PONG-PING-MAC-TO-DELL-001" in first["expected_echo_command"]

    # CLI handoff increments sequence_number and preserves existing routines_for_dell
    rc = cli_main([
        "handoff",
        "--root",
        str(tmp_path),
        "--from-node",
        "DELL_WINDOWS_LAB",
        "--to-node",
        "MAC_COMMAND_CENTER",
        "--ping-id",
        "PONG-PING-MAC-TO-DELL-001",
        "--note",
        "Sincronización confirmada en Dell Windows.",
    ])
    assert rc == 0
    out_handoff = json.loads(capsys.readouterr().out)
    assert out_handoff["sequence_number"] == 2
    assert len(out_handoff["routines_for_dell"]) == 1
    assert len(out_handoff["ping_history"]) == 2

    # CLI notify returns exit 0 and writes JSONL log
    rc_notify = cli_main([
        "notify",
        "--root",
        str(tmp_path),
        "--level",
        "ACTION_REQUIRED",
        "--title",
        "Revisión pendiente",
        "--summary",
        "Prueba de alerta automática desde CLI.",
        "--dry-run",
    ])
    assert rc_notify == 0
    out_notify = json.loads(capsys.readouterr().out)
    assert out_notify["delivery"]["status"] == "LOGGED_LOCAL_QUEUE"
