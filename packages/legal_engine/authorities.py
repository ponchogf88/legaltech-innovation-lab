"""Authority registry, receipt model, and offline mock authority adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from .models import Document, Submission

KNOWN_AUTHORITIES: dict[str, str] = {
    "tribunal-virtual": "Tribunal Virtual (Poder Judicial)",
    "sat": "SAT (Servicio de Administración Tributaria)",
    "registro-publico": "Registro Público de la Propiedad",
}


class UnknownAuthorityError(ValueError):
    """Raised when an authority key is not registered in KNOWN_AUTHORITIES."""


@dataclass(frozen=True)
class Receipt:
    """Synthetic filing acknowledgment returned by an AuthorityAdapter."""

    folio: str
    authority: str
    channel: str = "MOCK"
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submission_id: str = ""
    document_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize the receipt into JSON-safe primitives."""
        return {
            "folio": self.folio,
            "authority": self.authority,
            "channel": self.channel,
            "submitted_at": self.submitted_at.isoformat(),
            "submission_id": self.submission_id,
            "document_id": self.document_id,
        }


@runtime_checkable
class AuthorityAdapter(Protocol):
    """Protocol for authority submission connectors (always offline/mock in demo)."""

    authority_key: str
    channel: str

    def submit(self, submission: Submission, document: Document) -> Receipt:
        """Submit an approved document and return an authority receipt."""
        ...


class MockAuthority:
    """Offline synthetic authority adapter generating MOCK- prefixed folios."""

    channel: str = "MOCK"

    def __init__(self, authority_key: str = "tribunal-virtual") -> None:
        if authority_key not in KNOWN_AUTHORITIES:
            raise UnknownAuthorityError(
                f"Unknown authority '{authority_key}'. Expected one of: {sorted(KNOWN_AUTHORITIES)}"
            )
        self.authority_key = authority_key

    def submit(self, submission: Submission, document: Document) -> Receipt:
        """Simulate submission strictly offline without any external network I/O."""
        token = uuid4().hex[:10].upper()
        folio = f"MOCK-{token}"
        return Receipt(
            folio=folio,
            authority=self.authority_key,
            channel=self.channel,
            submitted_at=datetime.now(timezone.utc),
            submission_id=submission.id,
            document_id=document.id,
        )


def get_authority(authority_key: str) -> AuthorityAdapter:
    """Return a validated authority adapter for the given registry key."""
    if not isinstance(authority_key, str) or authority_key.strip() not in KNOWN_AUTHORITIES:
        raise UnknownAuthorityError(
            f"Unknown authority '{authority_key}'. Allowed keys: {sorted(KNOWN_AUTHORITIES)}"
        )
    return MockAuthority(authority_key=authority_key.strip())
