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
from .continuity import (
    CHECKPOINT_FILENAME,
    CLOCK_DURATION_HOURS,
    CLOCK_DURATION_SECONDS,
    CLOCK_FILENAME,
    CONFIRMED_START_ISO,
    REQUIRED_TASK_FIELDS,
    STATE_FILENAME,
    VALID_TASK_STATUSES,
    compute_clock_status,
    format_duration_hms,
    identify_next_unblocked_task,
    init_72h_clock,
    inspect_git_state,
    load_or_init_72h_clock,
    save_checkpoint,
    validate_task_queue,
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
    "CHECKPOINT_FILENAME",
    "CLOCK_DURATION_HOURS",
    "CLOCK_DURATION_SECONDS",
    "CLOCK_FILENAME",
    "CONFIRMED_START_ISO",
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
    "REQUIRED_TASK_FIELDS",
    "Receipt",
    "ReviewError",
    "ReviewQueue",
    "SQLiteRepository",
    "STATE_FILENAME",
    "Submission",
    "SubmissionBlockedError",
    "SubmissionState",
    "TEMPLATES",
    "UnknownAuthorityError",
    "VALID_TASK_STATUSES",
    "compute_clock_status",
    "compute_deadlines",
    "create_server",
    "format_duration_hms",
    "get_authority",
    "handle_api_request",
    "identify_next_unblocked_task",
    "init_72h_clock",
    "inspect_git_state",
    "intake_matter",
    "list_upcoming",
    "load_or_init_72h_clock",
    "render_document",
    "run_server",
    "save_checkpoint",
    "submit",
    "transition",
    "validate_task_queue",
]
