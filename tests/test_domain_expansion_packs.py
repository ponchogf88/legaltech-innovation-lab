"""Tests for synthetic Corporate Governance and Regulatory Compliance expansion packs."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from legal_engine.authorities import get_authority
from legal_engine.deadlines import compute_deadlines
from legal_engine.documents import TEMPLATES, render_document
from legal_engine.intake import intake_matter
from legal_engine.models import Submission, SubmissionState
from legal_engine.review import ReviewQueue
from legal_engine.submissions import submit

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_corporate_governance_expansion_pack_end_to_end() -> None:
    assert "acta_asamblea_corporativa" in TEMPLATES
    fixture_path = REPO_ROOT / "examples" / "matter_gobierno_corporativo_sintetico.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))

    matter = intake_matter(raw)
    assert matter.id == "CORP-SINT-2026-001"
    assert matter.authority == "registro-publico"

    deadlines = compute_deadlines(matter, reference_date=date(2026, 11, 18))
    assert len(deadlines) >= 2

    document = render_document(matter, template_key="acta_asamblea_corporativa")
    assert "ACTA DE ASAMBLEA GENERAL ORDINARIA DE ACCIONISTAS" in document.content
    assert "FM-SINT-2026-4410" in document.content
    assert "[DOCUMENTO SINTÉTICO" in document.content

    queue = ReviewQueue()
    submission = Submission(
        id="SUB-CORP-001",
        matter_id=matter.id,
        document_id=document.id,
        state=SubmissionState.DRAFT,
    )
    queue.submit_for_review(submission, actor="dike-drafting")
    queue.approve(submission, reviewer="Lic. Corporativo Sintético")

    receipt = submit(
        submission,
        document,
        get_authority(matter.authority),
        actor="Lic. Corporativo Sintético",
    )
    assert receipt.folio.startswith("MOCK-")
    assert receipt.authority == "registro-publico"


def test_regulatory_compliance_expansion_pack_end_to_end() -> None:
    assert "contestacion_requerimiento_regulatorio" in TEMPLATES
    fixture_path = REPO_ROOT / "examples" / "matter_cumplimiento_regulatorio_sintetico.json"
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))

    matter = intake_matter(raw)
    assert matter.id == "REG-SINT-2026-001"
    assert matter.authority == "sat"

    deadlines = compute_deadlines(matter, reference_date=date(2026, 11, 18))
    assert any("fiscal" in item.title.lower() for item in deadlines)

    document = render_document(matter, template_key="contestacion_requerimiento_regulatorio")
    assert "CONTESTACIÓN A REQUERIMIENTO DE CUMPLIMIENTO REGULATORIO Y FISCAL" in document.content
    assert "XAXX010101000" in document.content
    assert "OF-SINT-SAT-2026-019" in document.content
    assert "[DOCUMENTO SINTÉTICO" in document.content

    queue = ReviewQueue()
    submission = Submission(
        id="SUB-REG-001",
        matter_id=matter.id,
        document_id=document.id,
        state=SubmissionState.DRAFT,
    )
    queue.submit_for_review(submission, actor="dike-drafting")
    queue.approve(submission, reviewer="Lic. Cumplimiento Sintético")

    receipt = submit(
        submission,
        document,
        get_authority(matter.authority),
        actor="Lic. Cumplimiento Sintético",
    )
    assert receipt.folio.startswith("MOCK-")
    assert receipt.authority == "sat"
