"""Strict state machine and human-approval gate for legal submissions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .authorities import AuthorityAdapter, Receipt
from .models import Document, Submission, SubmissionState

if TYPE_CHECKING:
    from .audit import AuditLog

ALLOWED_TRANSITIONS: dict[SubmissionState, set[SubmissionState]] = {
    SubmissionState.DRAFT: {SubmissionState.IN_REVIEW},
    SubmissionState.IN_REVIEW: {SubmissionState.APPROVED, SubmissionState.DRAFT},
    SubmissionState.APPROVED: {SubmissionState.SUBMITTED},
    SubmissionState.SUBMITTED: {SubmissionState.RECEIPTED},
    SubmissionState.RECEIPTED: set(),
}


class SubmissionBlockedError(RuntimeError):
    """Raised when submission is attempted without prior human approval or valid document match."""


class InvalidTransitionError(RuntimeError):
    """Raised when a requested SubmissionState transition violates ALLOWED_TRANSITIONS."""


def transition(
    submission: Submission,
    to_state: SubmissionState | str,
    actor: str = "system",
    note: str = "",
) -> Submission:
    """Validate and execute a SubmissionState transition while appending audit history."""
    try:
        target = to_state if isinstance(to_state, SubmissionState) else SubmissionState(str(to_state))
    except ValueError as exc:
        raise InvalidTransitionError(f"Unknown target state: {to_state}") from exc

    allowed = ALLOWED_TRANSITIONS.get(submission.state, set())
    if target not in allowed:
        raise InvalidTransitionError(
            f"Transition {submission.state.value} -> {target.value} is not allowed."
        )

    clean_actor = actor.strip() if isinstance(actor, str) and actor.strip() else "system"
    submission.history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "from": submission.state.value,
            "to": target.value,
            "actor": clean_actor,
            "note": note,
        }
    )
    submission.state = target
    return submission


def submit(
    submission: Submission,
    document: Document,
    adapter: AuthorityAdapter,
    actor: str,
    audit: AuditLog | None = None,
) -> Receipt:
    """Submit an APPROVED submission through an AuthorityAdapter and record receipt."""
    clean_actor = actor.strip() if isinstance(actor, str) else ""
    if not clean_actor:
        raise SubmissionBlockedError("An explicit actor identifier is required to submit.")

    if submission.state is not SubmissionState.APPROVED:
        if audit is not None:
            audit.record(
                actor=clean_actor,
                action="submission_blocked",
                matter_id=submission.matter_id,
                details={
                    "submission_id": submission.id,
                    "state": submission.state.value,
                    "reason": "Human approval (APPROVED) is mandatory before authority submission.",
                },
            )
        raise SubmissionBlockedError(
            f"Submission '{submission.id}' is in state '{submission.state.value}'; "
            "human approval (APPROVED) is mandatory before submission."
        )

    if document.id != submission.document_id or document.matter_id != submission.matter_id:
        raise SubmissionBlockedError(
            f"Document '{document.id}' does not match submission '{submission.id}'."
        )

    transition(
        submission,
        SubmissionState.SUBMITTED,
        actor=clean_actor,
        note=f"Dispatching to authority '{adapter.authority_key}' via {adapter.channel}",
    )

    receipt = adapter.submit(submission, document)
    if receipt.folio:
        submission.receipt_folio = receipt.folio
        transition(
            submission,
            SubmissionState.RECEIPTED,
            actor=clean_actor,
            note=f"Receipt folio assigned: {receipt.folio}",
        )

    if audit is not None:
        audit.record(
            actor=clean_actor,
            action="submission_sent",
            matter_id=submission.matter_id,
            details={
                "submission_id": submission.id,
                "document_id": document.id,
                "authority": receipt.authority,
                "channel": receipt.channel,
                "folio": receipt.folio,
                "state": submission.state.value,
            },
        )

    return receipt
