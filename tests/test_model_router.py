"""Unit tests for the Smart Multi-Model Router and 4-Stratum Historical Jurist Council."""

from __future__ import annotations

import pytest

from legal_engine.router import (
    COUNCIL_PERSONAS,
    STRATA_CATALOG,
    UnknownTaskRouteError,
    list_council_personas,
    route_legal_task,
)
from legal_engine.security import SecurityViolationError


def test_strata_catalog_and_council_personas_preserve_zero_anachronism_rules() -> None:
    assert set(STRATA_CATALOG.keys()) == {"STRATUM_I", "STRATUM_II", "STRATUM_III", "STRATUM_IV"}
    assert len(COUNCIL_PERSONAS) == 15

    stratum_ii = list_council_personas("STRATUM_II")
    ids_ii = {p["id"] for p in stratum_ii}
    assert {"ciceron", "ulpiano", "justiniano", "julio_cesar", "alejandro_magno"} == ids_ii

    for stratum in STRATA_CATALOG.values():
        assert stratum["visual_style"]
        assert stratum["epoch_rule"]


def test_smart_model_router_assigns_optimal_provider_by_task_and_volume() -> None:
    ocr_decision = route_legal_task("ocr_mass", document_pages=40)
    assert ocr_decision.provider == "Google Gemini"
    assert ocr_decision.persona_id == "hermes"
    assert ocr_decision.estimated_relative_cost == "ultra_low"
    assert ocr_decision.telemetry_span["pii_redacted"] is True

    usura_decision = route_legal_task("usura_analysis")
    assert usura_decision.provider == "Anthropic Claude"
    assert usura_decision.persona_id == "ulpiano"
    assert usura_decision.stratum_id == "STRATUM_II"

    deadline_decision = route_legal_task("deadline_calc")
    assert deadline_decision.provider == "OpenAI"
    assert deadline_decision.persona_id == "julio_cesar"

    # Volume escalation overrides smaller text models when >80 scanned pages
    massive_case = route_legal_task("json_structuring", persona_id="atenea", document_pages=180)
    assert massive_case.provider == "Google Gemini"
    assert "180 fojas" in massive_case.rationale

    # High-complexity escalation lifts OpenAI orchestrator task to Claude deep legal reasoning
    complex_case = route_legal_task("deadline_calc", complexity="high")
    assert complex_case.provider == "Anthropic Claude"


def test_smart_model_router_rejects_pii_and_unknown_inputs() -> None:
    blocked_rfc = "GODE" + "561231" + "GR8"
    with pytest.raises(SecurityViolationError, match="RFC_PATTERN"):
        route_legal_task("usura_analysis", payload_preview=f"RFC cliente {blocked_rfc}")

    with pytest.raises(UnknownTaskRouteError):
        route_legal_task("")

    with pytest.raises(UnknownTaskRouteError):
        route_legal_task("usura_analysis", persona_id="agente_inexistente")
