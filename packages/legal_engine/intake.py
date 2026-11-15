"""Matter intake validation and optional synthetic-only security gate."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
import json
import re
from typing import Any
from uuid import uuid4

from .authorities import KNOWN_AUTHORITIES
from .models import Matter

try:
    from .security import SecurityViolationError, assert_synthetic_and_safe
except ImportError:  # pragma: no cover - optional prior to Workstream C merge
    class _MissingSecurityError(Exception):
        pass

    SecurityViolationError = _MissingSecurityError  # type: ignore[assignment, misc]
    assert_synthetic_and_safe = None  # type: ignore[assignment]

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class IntakeValidationError(ValueError):
    """Raised when an incoming matter payload fails structural or domain validation."""


def _run_security_gate(data: Mapping[str, Any]) -> None:
    if assert_synthetic_and_safe is None:
        return
    try:
        assert_synthetic_and_safe(dict(data))
    except TypeError:
        serialized = json.dumps(dict(data), ensure_ascii=False, default=str)
        assert_synthetic_and_safe(serialized)


def _require_non_empty_str(data: Mapping[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise IntakeValidationError(f"Field '{field_name}' must be a non-empty string.")
    return value.strip()


def _parse_documents_needed(raw: Any) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise IntakeValidationError("Field 'documents_needed' must be a list of strings.")
    cleaned: list[str] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, str) or not item.strip():
            raise IntakeValidationError(
                f"Field 'documents_needed[{idx}]' must be a non-empty string."
            )
        cleaned.append(item.strip())
    return cleaned


def _parse_filing_date(raw: Any) -> date | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, datetime):
        raise IntakeValidationError("Field 'filing_date' must be an ISO date (YYYY-MM-DD).")
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        candidate = raw.strip()
        if not candidate:
            return None
        if not _ISO_DATE_RE.fullmatch(candidate):
            raise IntakeValidationError(
                f"Field 'filing_date' must match ISO format YYYY-MM-DD, got '{raw}'."
            )
        try:
            return date.fromisoformat(candidate)
        except ValueError as exc:
            raise IntakeValidationError(f"Invalid calendar date for 'filing_date': '{raw}'.") from exc
    raise IntakeValidationError("Field 'filing_date' must be an ISO YYYY-MM-DD string or null.")


def intake_matter(data: dict[str, Any], matter_id: str | None = None) -> Matter:
    """Validate and construct a synthetic Matter from raw intake payload."""
    if not isinstance(data, Mapping):
        raise IntakeValidationError("Intake payload must be a JSON object/dictionary.")

    _run_security_gate(data)

    client_name = _require_non_empty_str(data, "client_name")
    matter_type = _require_non_empty_str(data, "matter_type")
    facts = _require_non_empty_str(data, "facts")
    authority = _require_non_empty_str(data, "authority")
    if authority not in KNOWN_AUTHORITIES:
        raise IntakeValidationError(
            f"Unknown authority '{authority}'. Allowed authorities: {sorted(KNOWN_AUTHORITIES)}"
        )

    documents_needed = _parse_documents_needed(data.get("documents_needed"))
    filing_date = _parse_filing_date(data.get("filing_date"))

    if matter_id is not None:
        if not isinstance(matter_id, str) or not matter_id.strip():
            raise IntakeValidationError("Explicit 'matter_id' must be a non-empty string.")
        resolved_id = matter_id.strip()
    elif isinstance(data.get("id"), str) and data["id"].strip():
        resolved_id = data["id"].strip()
    else:
        resolved_id = f"MAT-{uuid4().hex[:8].upper()}"

    return Matter(
        id=resolved_id,
        client_name=client_name,
        matter_type=matter_type,
        authority=authority,
        facts=facts,
        documents_needed=documents_needed,
        filing_date=filing_date,
    )
