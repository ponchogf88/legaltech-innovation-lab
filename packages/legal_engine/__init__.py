"""Human-in-the-Loop synthetic LegalTech workflow engine."""

from __future__ import annotations

from .api import create_server, handle_api_request, run_server
from .audit import AuditLog
from .authorities import (
    KNOWN_AUTHORITIES,
    AuthorityAdapter,
    MockAuthority,
    Receipt,
    UnknownAuthorityError,
    get_authority,
)
from .deadlines import DEFAULT_DEADLINE_RULES, Deadline, compute_deadlines, list_upcoming
from .documents import DEFAULT_TEMPLATES_DIR, TEMPLATES, DocumentRenderError, render_document
from .intake import IntakeValidationError, intake_matter
from .models import Document, EvidenceItem, Matter, Submission, SubmissionState
from .review import ReviewError, ReviewQueue
from .storage import SQLiteRepository
from .submissions import (
    ALLOWED_TRANSITIONS,
    InvalidTransitionError,
    SubmissionBlockedError,
    submit,
    transition,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ALLOWED_TRANSITIONS",
    "AuditLog",
    "AuthorityAdapter",
    "DEFAULT_DEADLINE_RULES",
    "DEFAULT_TEMPLATES_DIR",
    "Deadline",
    "Document",
    "DocumentRenderError",
    "EvidenceItem",
    "IntakeValidationError",
    "InvalidTransitionError",
    "KNOWN_AUTHORITIES",
    "Matter",
    "MockAuthority",
    "Receipt",
    "ReviewError",
    "ReviewQueue",
    "SQLiteRepository",
    "Submission",
    "SubmissionBlockedError",
    "SubmissionState",
    "TEMPLATES",
    "UnknownAuthorityError",
    "compute_deadlines",
    "create_server",
    "get_authority",
    "handle_api_request",
    "intake_matter",
    "list_upcoming",
    "render_document",
    "run_server",
    "submit",
    "transition",
]
