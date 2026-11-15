"""Core domain models for the synthetic Human-in-the-Loop LegalTech engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _coerce_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value)
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
    raise TypeError(f"Expected datetime or ISO string, got {type(value).__name__}")


def _coerce_optional_date(value: date | datetime | str | None) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"Expected date, ISO string, or None, got {type(value).__name__}")


class SubmissionState(str, Enum):
    """Lifecycle states enforcing human approval before submission."""

    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    RECEIPTED = "RECEIPTED"


@dataclass
class Matter:
    """Represents a synthetic legal matter entered through intake."""

    id: str
    client_name: str
    matter_type: str
    authority: str
    facts: str
    documents_needed: list[str] = field(default_factory=list)
    filing_date: date | None = None
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if self.documents_needed is None:
            self.documents_needed = []
        else:
            self.documents_needed = [str(item) for item in self.documents_needed]
        self.filing_date = _coerce_optional_date(self.filing_date)
        self.created_at = _coerce_datetime(self.created_at)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the matter into JSON-safe primitives."""
        return {
            "id": self.id,
            "client_name": self.client_name,
            "matter_type": self.matter_type,
            "authority": self.authority,
            "facts": self.facts,
            "documents_needed": list(self.documents_needed),
            "filing_date": self.filing_date.isoformat() if self.filing_date else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Document:
    """Represents a rendered synthetic legal draft linked to a matter."""

    id: str
    matter_id: str
    template_name: str
    content: str
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        self.created_at = _coerce_datetime(self.created_at)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the rendered document into JSON-safe primitives."""
        return {
            "id": self.id,
            "matter_id": self.matter_id,
            "template_name": self.template_name,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Submission:
    """Tracks review, approval, and filing state of a rendered document."""

    id: str
    matter_id: str
    document_id: str
    state: SubmissionState = SubmissionState.DRAFT
    receipt_folio: str | None = None
    reviewer: str | None = None
    rejection_reason: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.state, SubmissionState):
            self.state = SubmissionState(str(self.state))
        if self.history is None:
            self.history = []
        else:
            self.history = [dict(entry) for entry in self.history]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the submission and transition history into JSON-safe primitives."""
        return {
            "id": self.id,
            "matter_id": self.matter_id,
            "document_id": self.document_id,
            "state": self.state.value,
            "receipt_folio": self.receipt_folio,
            "reviewer": self.reviewer,
            "rejection_reason": self.rejection_reason,
            "history": [dict(entry) for entry in self.history],
        }


@dataclass
class EvidenceItem:
    """Structured legal analysis item requiring mandatory human verification."""

    id: str
    matter_id: str
    title: str
    kind: str
    source_pages: str | list[int]
    extracted_fact: str
    legal_conclusion: str
    requires_human_verification: bool = True
    verification_note: str = ""

    def __post_init__(self) -> None:
        self.requires_human_verification = bool(self.requires_human_verification)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the evidence item into JSON-safe primitives."""
        return {
            "id": self.id,
            "matter_id": self.matter_id,
            "title": self.title,
            "kind": self.kind,
            "source_pages": (
                list(self.source_pages)
                if isinstance(self.source_pages, list)
                else self.source_pages
            ),
            "extracted_fact": self.extracted_fact,
            "legal_conclusion": self.legal_conclusion,
            "requires_human_verification": self.requires_human_verification,
            "verification_note": self.verification_note,
        }
