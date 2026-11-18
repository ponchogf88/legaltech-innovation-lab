"""Alimony deposit slip workflow, UAPA appointment scheduling, and PJENL official channels."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any
from uuid import uuid4

from .security import assert_synthetic_and_safe

DEPOSIT_STAGES: tuple[str, ...] = (
    "CONSIGNADO",
    "PROMOCION_AUTORIZADA",
    "CITA_UAPA_AGENDADA",
    "COMPARECENCIA_LEVANTADA",
    "TESORERIA_LIQUIDADO",
)

APPOINTMENT_CHANNELS: tuple[str, ...] = (
    "TRIBUNAL_VIRTUAL",
    "WHATSAPP_PJENL",
    "TELEFONO_PJENL",
    "PRESENCIAL_UAPA",
)

PJENL_OFFICIAL_CHANNELS: dict[str, str] = {
    "institution": "Poder Judicial del Estado de Nuevo León (PJENL)",
    "portal": "https://www.pjenl.gob.mx",
    "tribunal_virtual_url": "https://tribunalvirtual.pjenl.gob.mx/",
    "appointment_menu_path": "Mis trámites > Citas > Agendar",
    "whatsapp_assistant": "81-8366-6781",
    "service_hours": "Lunes a viernes de 08:30 a 16:00 hrs",
    "administrative_unit": "Unidad de Asistencia Procesal y Administrativa (UAPA) / Juzgados Orales",
}


class AlimonyDepositError(ValueError):
    """Raised when an alimony deposit record or appointment violates domain/HITL rules."""


@dataclass(frozen=True)
class AlimonyDepositRecord:
    """Represents an alimony deposit slip lifecycle from court consignment to Treasury payout."""

    id: str
    matter_id: str
    beneficiary_name: str
    deposit_slip_folio: str
    amount_mxn: float
    court_unit: str
    channel: str
    stage: str
    appointment_folio: str | None = None
    appointment_datetime: str | None = None
    approved_by_lawyer: str | None = None
    client_checklist: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize record into a JSON-friendly dictionary."""
        return asdict(self)


def _require_str(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise AlimonyDepositError(f"Field '{field}' is required and must be a non-empty string.")
    return value.strip()


def create_alimony_deposit_record(raw: dict[str, Any]) -> AlimonyDepositRecord:
    """Validate synthetic safety and initialize an AlimonyDepositRecord."""
    if not isinstance(raw, dict):
        raise AlimonyDepositError("Deposit payload must be a dictionary.")

    assert_synthetic_and_safe(raw)

    record_id = _require_str(raw, "id")
    matter_id = _require_str(raw, "matter_id")
    beneficiary_name = _require_str(raw, "beneficiary_name")
    deposit_slip_folio = _require_str(raw, "deposit_slip_folio")
    court_unit = _require_str(raw, "court_unit")

    amount = raw.get("amount_mxn")
    if not isinstance(amount, (int, float)) or isinstance(amount, bool) or float(amount) <= 0:
        raise AlimonyDepositError("amount_mxn must be a positive number.")

    channel = str(raw.get("channel") or "TRIBUNAL_VIRTUAL").strip()
    if channel not in APPOINTMENT_CHANNELS:
        raise AlimonyDepositError(
            f"Invalid channel {channel!r}; allowed: {APPOINTMENT_CHANNELS}"
        )

    stage = str(raw.get("stage") or "CONSIGNADO").strip()
    if stage not in DEPOSIT_STAGES:
        raise AlimonyDepositError(f"Invalid stage {stage!r}; allowed: {DEPOSIT_STAGES}")

    return AlimonyDepositRecord(
        id=record_id,
        matter_id=matter_id,
        beneficiary_name=beneficiary_name,
        deposit_slip_folio=deposit_slip_folio,
        amount_mxn=round(float(amount), 2),
        court_unit=court_unit,
        channel=channel,
        stage=stage,
    )


def schedule_uapa_deposit_appointment(
    record: AlimonyDepositRecord,
    *,
    lawyer_approver: str,
    channel: str = "TRIBUNAL_VIRTUAL",
    preferred_slot: str = "2026-11-20T10:30:00-06:00",
) -> AlimonyDepositRecord:
    """Schedule a mock UAPA / Palacio de Justicia appointment for deposit slip pickup.

    Requires explicit human lawyer approval before issuing a MOCK appointment folio and
    generating the client checklist for comparecencia + Treasury payout.
    """
    if not isinstance(lawyer_approver, str) or not lawyer_approver.strip():
        raise AlimonyDepositError(
            "Human lawyer approval (lawyer_approver) is mandatory before scheduling court appointments."
        )
    if channel not in APPOINTMENT_CHANNELS:
        raise AlimonyDepositError(
            f"Invalid channel {channel!r}; allowed: {APPOINTMENT_CHANNELS}"
        )
    if not isinstance(preferred_slot, str) or not preferred_slot.strip():
        raise AlimonyDepositError("preferred_slot must be a non-empty timestamp string.")

    assert_synthetic_and_safe({
        "lawyer_approver": lawyer_approver,
        "channel": channel,
        "preferred_slot": preferred_slot,
        "matter_id": record.matter_id,
    })

    token = uuid4().hex[:6].upper()
    mock_folio = f"MOCK-CITA-UAPA-{token}"
    checklist = (
        f"Acudir el {preferred_slot.strip()} a {record.court_unit} (Palacio de Justicia).",
        f"Presentar identificación oficial vigente y folio de cita simulada {mock_folio}.",
        f"Levantar comparecencia formal para entrega del billete {record.deposit_slip_folio} (${record.amount_mxn:,.2f} MXN).",
        "Pasar a Tesorería / Finanzas con el billete endosado para su cobro o abono directo a cuenta.",
    )

    return replace(
        record,
        channel=channel,
        stage="CITA_UAPA_AGENDADA",
        appointment_folio=mock_folio,
        appointment_datetime=preferred_slot.strip(),
        approved_by_lawyer=lawyer_approver.strip(),
        client_checklist=checklist,
    )
