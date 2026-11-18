"""Tests for OpenTelemetry structured span tracing and zero-PII enforcement."""

from __future__ import annotations

import re

import pytest

from legal_engine.authorities import get_authority
from legal_engine.documents import render_document
from legal_engine.intake import intake_matter
from legal_engine.models import Submission, SubmissionState
from legal_engine.review import ReviewQueue
from legal_engine.security import SecurityViolationError
from legal_engine.submissions import submit
from legal_engine.telemetry import TelemetryTracer, trace_span

_TRACEPARENT_RE = re.compile(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$")


def test_telemetry_w3c_traceparent_and_nested_workflow_spans() -> None:
    tracer = TelemetryTracer()
    queue = ReviewQueue()

    with trace_span("workflow.pipeline", {"matter.authority": "tribunal-virtual"}, tracer=tracer):
        with trace_span("intake.load_matter", {"stage": "intake"}, tracer=tracer):
            matter = intake_matter({
                "id": "TEL-SINT-2026-001",
                "client_name": "Consorcio Telemetry Sintético S.A.",
                "matter_type": "solicitud",
                "authority": "tribunal-virtual",
                "facts": "Prueba sintética de trazabilidad estructurada en flujo HITL.",
            })

        with trace_span("documents.render", {"template": "solicitud_general"}, tracer=tracer):
            doc = render_document(matter, template_key="solicitud_general")

        sub = Submission(
            id="SUB-TEL-001",
            matter_id=matter.id,
            document_id=doc.id,
            state=SubmissionState.DRAFT,
        )
        queue.submit_for_review(sub, actor="tel-bot")

        with trace_span("review.approve", {"reviewer_role": "abogado"}, tracer=tracer):
            queue.approve(sub, reviewer="Lic. Telemetry Sintético")

        with trace_span("submissions.submit", {"channel": "MOCK"}, tracer=tracer):
            receipt = submit(sub, doc, get_authority(matter.authority), actor="Lic. Telemetry Sintético")
            assert receipt.folio.startswith("MOCK-")

    spans = tracer.get_spans()
    assert len(spans) == 5

    by_name = {span.name: span for span in spans}
    root = by_name["workflow.pipeline"]
    assert root.parent_span_id is None
    assert _TRACEPARENT_RE.fullmatch(root.w3c_traceparent)
    assert root.attributes["pii_redacted"] is True
    assert root.status_code == "OK"

    for child_name in ("intake.load_matter", "documents.render", "review.approve", "submissions.submit"):
        child = by_name[child_name]
        assert child.trace_id == root.trace_id
        assert child.parent_span_id == root.span_id
        assert _TRACEPARENT_RE.fullmatch(child.w3c_traceparent)
        assert child.attributes["pii_redacted"] is True

    exported = tracer.export_spans()
    assert len(exported) == 5
    assert all("w3c_traceparent" in row for row in exported)

    tracer.clear()
    assert tracer.export_spans() == []


def test_telemetry_captures_errors_and_blocks_pii() -> None:
    tracer = TelemetryTracer()

    with pytest.raises(RuntimeError, match="boom"):
        with tracer.start_span("failing.step", {"step": "demo"}):
            raise RuntimeError("boom")

    recorded = tracer.get_spans()
    assert len(recorded) == 1
    assert recorded[0].status_code == "ERROR"
    assert recorded[0].attributes["error.type"] == "RuntimeError"

    # PII inside span attributes must raise SecurityViolationError before emitting
    blocked_rfc = "GODE" + "561231" + "GR8"
    with pytest.raises(SecurityViolationError, match="RFC_PATTERN"):
        with tracer.start_span("unsafe.step", {"client_rfc": blocked_rfc}):
            pass
