"""Human-in-the-Loop review queue managing approval and rejection transitions."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Submission, SubmissionState
from .submissions import InvalidTransitionError, transition


class ReviewError(RuntimeError):
    """Raised when a review queue operation violates review rules or state constraints."""


class ReviewQueue:
    """In-memory coordinator for human review workflows over Submission objects."""

    def __init__(self, submissions: Iterable[Submission] | None = None) -> None:
        self._items: dict[str, Submission] = {}
        if submissions is not None:
            for item in submissions:
                self._items[item.id] = item

    def register(self, submission: Submission) -> Submission:
        """Register or refresh a submission in the queue index without changing state."""
        self._items[submission.id] = submission
        return submission

    def submit_for_review(self, submission: Submission, actor: str = "system") -> Submission:
        """Move a DRAFT submission into IN_REVIEW so a human reviewer can inspect it."""
        try:
            transition(
                submission,
                SubmissionState.IN_REVIEW,
                actor=actor,
                note="Queued for mandatory human review",
            )
        except InvalidTransitionError as exc:
            raise ReviewError(str(exc)) from exc
        self._items[submission.id] = submission
        return submission

    def approve(
        self,
        submission: Submission,
        reviewer: str,
        note: str = "Approved by human reviewer",
    ) -> Submission:
        """Approve an IN_REVIEW submission, recording the human reviewer."""
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ReviewError("A non-empty reviewer name is required to approve a submission.")
        clean_reviewer = reviewer.strip()
        try:
            transition(
                submission,
                SubmissionState.APPROVED,
                actor=clean_reviewer,
                note=note,
            )
        except InvalidTransitionError as exc:
            raise ReviewError(str(exc)) from exc
        submission.reviewer = clean_reviewer
        submission.rejection_reason = None
        self._items[submission.id] = submission
        return submission

    def reject(self, submission: Submission, reviewer: str, reason: str) -> Submission:
        """Reject an IN_REVIEW submission back to DRAFT with reviewer and reason."""
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ReviewError("A non-empty reviewer name is required to reject a submission.")
        if not isinstance(reason, str) or not reason.strip():
            raise ReviewError("A non-empty rejection reason is required.")
        clean_reviewer = reviewer.strip()
        clean_reason = reason.strip()
        try:
            transition(
                submission,
                SubmissionState.DRAFT,
                actor=clean_reviewer,
                note=f"Rejected: {clean_reason}",
            )
        except InvalidTransitionError as exc:
            raise ReviewError(str(exc)) from exc
        submission.reviewer = clean_reviewer
        submission.rejection_reason = clean_reason
        self._items[submission.id] = submission
        return submission

    def pending(self) -> list[Submission]:
        """Return all submissions currently awaiting human review (IN_REVIEW)."""
        return [
            item for item in self._items.values() if item.state is SubmissionState.IN_REVIEW
        ]

    def get(self, submission_id: str) -> Submission | None:
        """Look up a tracked submission by ID."""
        return self._items.get(submission_id)
