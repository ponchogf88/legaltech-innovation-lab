"""Unit tests for legal_engine core workflow, HITL gate, deadlines, and hash-chained audit."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path

import pytest

from legal_engine.audit import AuditLog
from legal_engine.authorities import MockAuthority, UnknownAuthorityError, get_authority
from legal_engine.deadlines import compute_deadlines, list_upcoming
from legal_engine.documents import DocumentRenderError, render_document
from legal_engine.intake import IntakeValidationError, intake_matter
from legal_engine.models import Submission, SubmissionState
from legal_engine.review import ReviewError, ReviewQueue
from legal_engine.security import SecurityViolationError
from legal_engine.submissions import InvalidTransitionError, SubmissionBlockedError, submit, transition

VALID_SYNTHETIC_MATTER = {
    "client_name": "Corporativo Alfa Sintético S.A. de C.V.",
    "matter_type": "mercantil",
    "authority": "tribunal-virtual",
    "facts": "Se solicita desahogo de diligencias preparatorias en expediente sintético EXP-SINT-2026-001.",
    "documents_needed": [
        "Contrato marco sintético",
        "Estado de cuenta ficticio",
    ],
    "filing_date": "2026-11-15",
}


def test_submission_blocked_without_human_approval(tmp_path: Path) -> None:
    """Submitting a DRAFT or IN_REVIEW item must raise SubmissionBlockedError and log block."""
    matter = intake_matter(VALID_SYNTHETIC_MATTER, matter_id="EXP-SINT-2026-001")
    document = render_document(matter, "solicitud_general", document_id="DOC-TEST-001")
    submission = Submission(id="SUB-TEST-001", matter_id=matter.id, document_id=document.id)
    adapter = MockAuthority("tribunal-virtual")
    audit = AuditLog(tmp_path / "audit.jsonl")

    with pytest.raises(SubmissionBlockedError):
        submit(submission, document, adapter, actor="agent-hermes", audit=audit)
    assert submission.state is SubmissionState.DRAFT

    queue = ReviewQueue()
    queue.submit_for_review(submission, actor="agent-apollo")
    assert submission.state is SubmissionState.IN_REVIEW

    with pytest.raises(SubmissionBlockedError):
        submit(submission, document, adapter, actor="agent-hermes", audit=audit)
    assert submission.state is SubmissionState.IN_REVIEW

    entries = audit.read_entries()
    assert len(entries) == 2
    assert all(entry["action"] == "submission_blocked" for entry in entries)
    assert audit.verify_integrity() is True


def test_approve_then_submit_issues_mock_receipt(tmp_path: Path) -> None:
    """Only APPROVED submissions can transition through SUBMITTED -> RECEIPTED via MockAuthority."""
    matter = intake_matter(VALID_SYNTHETIC_MATTER, matter_id="EXP-SINT-2026-002")
    document = render_document(matter, "escrito_presentacion", document_id="DOC-TEST-002")
    submission = Submission(id="SUB-TEST-002", matter_id=matter.id, document_id=document.id)

    queue = ReviewQueue()
    queue.submit_for_review(submission, actor="agent-apollo")
    queue.approve(submission, reviewer="Lic. Prueba Sintética")
    assert submission.state is SubmissionState.APPROVED

    audit = AuditLog(tmp_path / "audit.jsonl")
    receipt = submit(
        submission,
        document,
        get_authority(matter.authority),
        actor="Lic. Prueba Sintética",
        audit=audit,
    )
    assert receipt.folio.startswith("MOCK-")
    assert receipt.channel == "MOCK"
    assert submission.state is SubmissionState.RECEIPTED
    assert submission.receipt_folio == receipt.folio
    assert audit.verify_integrity() is True


def test_reject_returns_to_draft_and_requires_reason() -> None:
    """Rejecting an IN_REVIEW submission returns it to DRAFT and records reviewer & reason."""
    matter = intake_matter(VALID_SYNTHETIC_MATTER, matter_id="EXP-SINT-2026-003")
    submission = Submission(id="SUB-TEST-003", matter_id=matter.id, document_id="DOC-X")
    queue = ReviewQueue()
    queue.submit_for_review(submission)

    with pytest.raises(ReviewError):
        queue.reject(submission, reviewer="Lic. Revisor", reason="   ")

    queue.reject(submission, reviewer="Lic. Revisor", reason="Falta acreditar personalidad")
    assert submission.state is SubmissionState.DRAFT
    assert submission.rejection_reason == "Falta acreditar personalidad"
    assert queue.pending() == []


def test_intake_validation_and_security_gate() -> None:
    """Intake rejects missing fields, bad dates, unknown authorities, and PII."""
    for missing in ("client_name", "matter_type", "authority", "facts"):
        bad = {k: v for k, v in VALID_SYNTHETIC_MATTER.items() if k != missing}
        with pytest.raises(IntakeValidationError):
            intake_matter(bad)

    with pytest.raises(IntakeValidationError):
        intake_matter({**VALID_SYNTHETIC_MATTER, "authority": "desconocida"})

    with pytest.raises(IntakeValidationError):
        intake_matter({**VALID_SYNTHETIC_MATTER, "filing_date": "15/11/2026"})

    # Security gate rejects real-case marker constructed dynamically
    unsafe_case = "920" + "/2025"
    with pytest.raises(SecurityViolationError):
        intake_matter({**VALID_SYNTHETIC_MATTER, "facts": f"Expediente {unsafe_case}"})


def test_invalid_state_transition_raises() -> None:
    """Direct jump from DRAFT to SUBMITTED must fail loudly."""
    submission = Submission(id="SUB-ERR", matter_id="MAT-ERR", document_id="DOC-ERR")
    with pytest.raises(InvalidTransitionError):
        transition(submission, SubmissionState.SUBMITTED, actor="tester")


def test_document_render_watermarked_and_strict() -> None:
    """Rendered documents include synthetic watermark and fail on unknown template."""
    matter = intake_matter(VALID_SYNTHETIC_MATTER, matter_id="EXP-SINT-2026-004")
    doc = render_document(matter, template_key="solicitud_general")
    assert "DOCUMENTO SINTÉTICO" in doc.content
    assert matter.client_name in doc.content

    with pytest.raises(DocumentRenderError):
        render_document(matter, template_key="inexistente")


def test_deadlines_and_unknown_authority() -> None:
    """Deadlines compute accurately and unknown authorities raise UnknownAuthorityError."""
    matter = intake_matter(VALID_SYNTHETIC_MATTER, matter_id="EXP-SINT-2026-005")
    deadlines = compute_deadlines(matter, reference_date=date(2026, 11, 15))
    assert len(deadlines) == 3
    assert deadlines[0].due_date == date(2026, 11, 18)
    upcoming = list_upcoming([matter], within_days=10, reference_date=date(2026, 11, 15))
    assert [d.days_remaining for d in upcoming] == [3, 8]

    with pytest.raises(UnknownAuthorityError):
        get_authority("not-registered")


def test_audit_log_detects_tampering(tmp_path: Path) -> None:
    """Modifying an entry in the JSONL log invalidates the SHA-256 hash chain."""
    log_path = tmp_path / "audit.jsonl"
    log = AuditLog(log_path)
    log.record("hermes", "intake", "EXP-SINT-1", {"step": 1})
    log.record("apollo", "render", "EXP-SINT-1", {"step": 2})
    assert log.verify_integrity() is True

    lines = log_path.read_text(encoding="utf-8").splitlines()
    tampered = json.loads(lines[0])
    tampered["actor"] = "attacker"
    lines[0] = json.dumps(tampered)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert log.verify_integrity() is False


def test_cli_demo_and_security_check(capsys: pytest.CaptureFixture[str]) -> None:
    """CLI demo, --stop-before-submit, and security-check execute cleanly with non-empty output."""
    from legal_engine.cli import main as cli_main

    repo_root = Path(__file__).resolve().parents[1]

    rc_demo = cli_main(["demo"])
    out_demo = capsys.readouterr().out
    assert rc_demo == 0
    assert "Approved & submitted via MOCK" in out_demo
    assert "Audit chain integrity: VALID" in out_demo

    rc_safe = cli_main(["demo", "--stop-before-submit"])
    out_safe = capsys.readouterr().out
    assert rc_safe == 0
    assert "Human-in-the-loop gate verified (stopped before submit)" in out_safe

    rc_sec = cli_main(["security-check", "--root", str(repo_root)])
    out_sec = capsys.readouterr().out
    assert rc_sec == 0
    payload = json.loads(out_sec)
    assert payload["scan_clean"] is True
    assert payload["governance_ready"] is True
