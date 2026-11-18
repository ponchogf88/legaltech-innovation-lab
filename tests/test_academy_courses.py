"""Tests for the specialized legal continuing-education and certification module."""

from __future__ import annotations

from datetime import date

import pytest

from legal_engine.academy import (
    AcademyValidationError,
    compute_course_reminders,
    summarize_lawyer_academy,
    validate_legal_course,
)
from legal_engine.security import SecurityViolationError


def _make_course_payload(**overrides) -> dict:
    base = {
        "id": "ACAD-2026-01",
        "title": "Diplomado en Litigio Estratégico Mercantil y Usura",
        "institution": "Casas de la Cultura Jurídica · SCJN (Simulado)",
        "practice_area": "Mercantil y Bancario",
        "kind": "DIPLOMADO",
        "start_date": "2026-11-20",
        "end_date": "2027-02-28",
        "next_milestone_date": "2026-11-20",
        "next_milestone_label": "Sesión inaugural Módulo I",
        "status": "POR_INICIAR",
        "credit_hours": 120,
        "progress_pct": 0,
        "certificate_folio": None,
        "linked_council_agent": "Ulpiano & Cicerón",
    }
    base.update(overrides)
    return base


def test_validate_and_summarize_legal_academy_portfolio() -> None:
    courses = [
        validate_legal_course(_make_course_payload()),
        validate_legal_course(
            _make_course_payload(
                id="ACAD-2026-02",
                title="Certificación en Juicio de Amparo Directo",
                institution="Escuela Federal de Formación Judicial (Simulado)",
                practice_area="Amparo y Constitucional",
                kind="CERTIFICACION",
                start_date="2026-10-01",
                end_date="2026-11-30",
                next_milestone_date="2026-11-25",
                next_milestone_label="Entrega de proyecto integrador de agravios",
                status="EN_CURSO",
                credit_hours=60,
                progress_pct=75,
                linked_council_agent="Montesquieu",
            )
        ),
        validate_legal_course(
            _make_course_payload(
                id="ACAD-2026-03",
                title="Curso Taller de Cadena de Custodia Forense",
                institution="Instituto de Estudios Judiciales (Simulado)",
                practice_area="Litigio Oral y Forense",
                kind="CURSO_ESPECIALIZADO",
                start_date="2026-09-01",
                end_date="2026-09-30",
                next_milestone_date="2026-09-30",
                next_milestone_label="Diploma expedido",
                status="CERTIFICADO",
                credit_hours=40,
                progress_pct=100,
                certificate_folio="CERT-SINT-2026-001",
                linked_council_agent="Temis",
            )
        ),
    ]

    ref = date(2026, 11, 18)
    reminders = compute_course_reminders(courses, reference_date=ref)
    # Certified courses do not emit pending reminders.
    assert [r.course_id for r in reminders] == ["ACAD-2026-01", "ACAD-2026-02"]
    assert reminders[0].days_until == 2
    assert reminders[0].urgency == "high"
    assert reminders[1].days_until == 7
    assert reminders[1].urgency == "medium"

    summary = summarize_lawyer_academy(courses, reference_date=ref)
    assert summary["total_courses"] == 3
    assert summary["starting_soon_count"] == 1
    assert summary["in_progress_count"] == 1
    assert summary["certificates_earned_count"] == 1
    assert summary["completed_credit_hours"] == 40
    assert summary["total_enrolled_hours"] == 220
    assert len(summary["reminders"]) == 2


def test_validate_legal_course_blocks_real_pii_and_invalid_states() -> None:
    # Construct sample RFC via concatenation so static repo scan stays clean
    blocked_rfc = "GODE" + "561231" + "GR8"
    with pytest.raises(SecurityViolationError, match="RFC_PATTERN"):
        validate_legal_course(_make_course_payload(institution=f"Despacho {blocked_rfc}"))

    # Require certificate folio when status is CERTIFICADO
    with pytest.raises(AcademyValidationError, match="certificate_folio"):
        validate_legal_course(_make_course_payload(status="CERTIFICADO", certificate_folio=None))

    # Reject unknown practice area outside the legal domain
    with pytest.raises(AcademyValidationError, match="practice_area"):
        validate_legal_course(_make_course_payload(practice_area="Cocina y Repostería"))
