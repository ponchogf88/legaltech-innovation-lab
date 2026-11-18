"""Tests for PJENL alimony deposit slip comparecencia and UAPA appointment workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from legal_engine.alimony import (
    PJENL_INFORMATICS_LIBRARY,
    PJENL_OFFICIAL_CHANNELS,
    AlimonyDepositError,
    create_alimony_deposit_record,
    schedule_uapa_deposit_appointment,
)
from legal_engine.documents import render_document
from legal_engine.intake import intake_matter
from legal_engine.security import SecurityViolationError


def _sample_deposit_payload(**overrides) -> dict:
    base = {
        "id": "DEP-SINT-2026-001",
        "matter_id": "ORAL-ALIM-SINT-2026-001",
        "beneficiary_name": "Elena Sofía Ejemplo Morales (Acreedora Sintética)",
        "deposit_slip_folio": "BD-SINT-8840",
        "amount_mxn": 12500.0,
        "court_unit": "UAPA Juzgados Orales Familiares (Palacio de Justicia Virtual)",
        "channel": "TRIBUNAL_VIRTUAL",
        "stage": "CONSIGNADO",
    }
    base.update(overrides)
    return base


def test_alimony_deposit_template_rendering_and_uapa_appointment_flow() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    example_path = repo_root / "examples" / "matter_alimentos_billete_sintetico.json"
    raw_matter = json.loads(example_path.read_text(encoding="utf-8"))

    matter = intake_matter(raw_matter)
    doc = render_document(matter, template_key="solicitud_entrega_billete_deposito")
    assert "ENTREGA DE BILLETE DE DEPÓSITO Y CITA PARA COMPARECENCIA" in doc.content
    assert "BD-SINT-8840" in doc.content
    assert "[DOCUMENTO SINTÉTICO" in doc.content

    record = create_alimony_deposit_record(_sample_deposit_payload())
    assert record.stage == "CONSIGNADO"
    assert PJENL_OFFICIAL_CHANNELS["whatsapp_assistant"] == "81-8366-6781"

    # Must block appointment confirmation if lawyer_approver is empty
    with pytest.raises(AlimonyDepositError, match="mandatory"):
        schedule_uapa_deposit_appointment(record, lawyer_approver="   ")

    scheduled = schedule_uapa_deposit_appointment(
        record,
        lawyer_approver="Lic. Valeria Mendoza (Simulado)",
        channel="WHATSAPP_PJENL",
        preferred_slot="2026-11-20T10:30:00-06:00",
    )
    assert scheduled.stage == "CITA_UAPA_AGENDADA"
    assert scheduled.channel == "WHATSAPP_PJENL"
    assert scheduled.appointment_folio is not None
    assert scheduled.appointment_folio.startswith("MOCK-CITA-UAPA-")
    assert len(scheduled.client_checklist) == 4
    assert any("Tesorería" in item for item in scheduled.client_checklist)
    assert any("comparecencia" in item.lower() for item in scheduled.client_checklist)


def test_alimony_deposit_rejects_pii_and_invalid_channels() -> None:
    blocked_rfc = "GODE" + "561231" + "GR8"
    with pytest.raises(SecurityViolationError, match="RFC_PATTERN"):
        create_alimony_deposit_record(_sample_deposit_payload(beneficiary_name=f"Persona {blocked_rfc}"))

    with pytest.raises(AlimonyDepositError, match="channel"):
        create_alimony_deposit_record(_sample_deposit_payload(channel="CANAL_DESCONOCIDO"))


def test_pjenl_informatics_library_completeness() -> None:
    pillars = {item["id"]: item for item in PJENL_INFORMATICS_LIBRARY["normative_pillars"]}
    for required_id in (
        "CPCNL-TV-44-87",
        "TV-CONVENIO-PDF",
        "ACUERDO-4-II-2014",
        "ACUERDO-1-II-2024",
        "ACUERDO-1-II-2025-FEJUD",
        "ACUERDO-2-II-2025-SOBRE",
        "ACUERDO-7-2022-NO-PARTES",
    ):
        assert required_id in pillars

    capabilities = PJENL_INFORMATICS_LIBRARY["power_user_capabilities"]
    assert len(capabilities) == 10
    assert any("Sobre Electrónico de Posiciones" in item["title"] for item in capabilities)
    assert PJENL_INFORMATICS_LIBRARY["training_and_support"]["helpdesk_email"] == "cst@pjenl.gob.mx"
