"""SQLite persistence round-trip tests for matters, documents, submissions, and evidence."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from legal_engine.documents import render_document
from legal_engine.intake import intake_matter
from legal_engine.models import EvidenceItem, Submission, SubmissionState
from legal_engine.review import ReviewQueue
from legal_engine.storage import SQLiteRepository


def test_sqlite_roundtrip_across_file_reopen(tmp_path: Path) -> None:
    """Data persisted to SQLite survives closing and reopening the database file."""
    db_path = tmp_path / "lab.db"
    matter = intake_matter(
        {
            "client_name": "Inmobiliaria Delta Sintética S.A.",
            "matter_type": "solicitud",
            "authority": "registro-publico",
            "facts": "Solicitud sintética de certificado de libertad de gravamen.",
            "documents_needed": ["Escritura sintética"],
            "filing_date": "2026-11-15",
        },
        matter_id="EXP-SINT-DB-001",
    )
    document = render_document(matter, template_key="solicitud_general", document_id="DOC-DB-001")
    submission = Submission(id="SUB-DB-001", matter_id=matter.id, document_id=document.id)
    queue = ReviewQueue()
    queue.submit_for_review(submission, actor="agent-apollo")
    queue.approve(submission, reviewer="Lic. Persistencia")

    evidence = EvidenceItem(
        id="EV-DB-001",
        matter_id=matter.id,
        title="Folio Mercantil Sintético",
        kind="Documento registral",
        source_pages=[1, 2],
        extracted_fact="Consta inscripción sintética de fecha 2026-01-10.",
        legal_conclusion="Requiere validación humana de vigencia antes de promover.",
        requires_human_verification=True,
        verification_note="Verificar sello registral sintético.",
    )

    with SQLiteRepository(db_path) as repo:
        repo.save_matter(matter)
        repo.save_document(document)
        repo.save_submission(submission)
        repo.save_evidence(evidence)

    with SQLiteRepository(db_path) as reopened:
        loaded_matter = reopened.get_matter("EXP-SINT-DB-001")
        assert loaded_matter is not None
        assert loaded_matter.client_name == "Inmobiliaria Delta Sintética S.A."
        assert loaded_matter.filing_date == date(2026, 11, 15)
        assert loaded_matter.documents_needed == ["Escritura sintética"]

        loaded_doc = reopened.get_document("DOC-DB-001")
        assert loaded_doc is not None
        assert "Inmobiliaria Delta Sintética" in loaded_doc.content

        loaded_sub = reopened.get_submission("SUB-DB-001")
        assert loaded_sub is not None
        assert loaded_sub.state is SubmissionState.APPROVED
        assert loaded_sub.reviewer == "Lic. Persistencia"
        assert len(loaded_sub.history) == 2

        loaded_ev = reopened.list_evidence("EXP-SINT-DB-001")
        assert len(loaded_ev) == 1
        assert loaded_ev[0].requires_human_verification is True
        assert loaded_ev[0].source_pages == [1, 2]
