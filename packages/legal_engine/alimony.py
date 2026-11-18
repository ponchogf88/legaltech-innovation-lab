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
    "helpdesk_email": "cst@pjenl.gob.mx",
    "helpdesk_phone": "(81) 2020-7751",
}

PJENL_INFORMATICS_LIBRARY: dict[str, Any] = {
    "statute_scope": "Código de Procedimientos Civiles de Nuevo León · Libro Séptimo, Segundo Título Especial (Arts. 44-87) + Arts. 21, 33, 52 y 78",
    "normative_pillars": (
        {
            "id": "CPCNL-TV-44-87",
            "title": "Segundo Título Especial 'Del Tribunal Virtual' (Arts. 44-87 CPCNL)",
            "source_url": "https://www.pjenl.gob.mx/Normativa/Codigos/",
        },
        {
            "id": "TV-CONVENIO-PDF",
            "title": "Convenio Electrónico de Uso (TVConvenio.pdf) y Política de Privacidad",
            "source_url": "https://tribunalvirtual.pjenl.gob.mx/htm/TVConvenio.pdf",
        },
        {
            "id": "ACUERDO-4-II-2014",
            "title": "Acuerdo General Conjunto 4-II/2014 (Administración Judicial Interna Tribunal Virtual)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2014/Acuerdo04-II.pdf",
        },
        {
            "id": "ACUERDO-1-II-2024",
            "title": "Acuerdo General Conjunto 1-II/2024 (Medios Electrónicos en Procesos Judiciales)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2024/Acuerdo01-II.pdf",
        },
        {
            "id": "ACUERDO-1-II-2025-FEJUD",
            "title": "Acuerdo General Conjunto 1-II/2025 (Firma Electrónica Avanzada FEJUD)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2025/Acuerdo01-II.pdf",
        },
        {
            "id": "ACUERDO-2-II-2025-SOBRE",
            "title": "Acuerdo General Conjunto 2-II/2025 (Sobre Electrónico de Posiciones)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2025/Acuerdo02-II.pdf",
        },
        {
            "id": "ACUERDO-7-2022-NO-PARTES",
            "title": "Acuerdos Generales 7/2022 y 8/2022 (Empleadores, Peritos y Auxiliares No-Partes)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/CJ/Pleno/Acuerdos/2022/Acuerdo07.pdf",
        },
        {
            "id": "ACUERDO-3-II-2015-COPIAS",
            "title": "Acuerdo General Conjunto 3-II/2015 (Copias Certificadas Electrónicas)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2015/Acuerdo03-II.pdf",
        },
        {
            "id": "ACUERDO-2-II-2017-EXHORTOS",
            "title": "Acuerdos Generales Conjuntos 5-II/2013 y 2-II/2017 (Exhortos Electrónicos)",
            "source_url": "https://www.pjenl.gob.mx/PoderJudicial/TSJ/Pleno/Acuerdos/2017/Acuerdo02-II.pdf",
        },
    ),
    "power_user_capabilities": (
        {
            "id": "CAP-01",
            "title": "Sobre Electrónico de Posiciones",
            "legal_basis": "Acuerdo General Conjunto 2-II/2025 (02/07/2025)",
            "operational_advantage": "Exhibición y resguardo cifrado de pliego de posiciones en confesional sin sobre de papel.",
        },
        {
            "id": "CAP-02",
            "title": "Firma Electrónica Judicial Avanzada (FEJUD) y FIEL SAT",
            "legal_basis": "Acuerdo General Conjunto 1-II/2025 y Acuerdo 7/2017",
            "operational_advantage": "Sustituye firma autógrafa con plena validez en promociones y resoluciones.",
        },
        {
            "id": "CAP-03",
            "title": "Oficios Electrónicos a Empleadores y Bancos No-Partes",
            "legal_basis": "Acuerdos Generales 7/2022 y 8/2022 (13/05/2022)",
            "operational_advantage": "Acelera retenciones y oficios de pensión alimenticia directo al patrón registrado.",
        },
        {
            "id": "CAP-04",
            "title": "Salvamento de Términos por Falla Técnica del Sistema",
            "legal_basis": "CPCNL Artículos 53 y 75",
            "operational_advantage": "Exige al juzgado recabar reporte del Administrador antes de tener por extemporáneo un término.",
        },
        {
            "id": "CAP-05",
            "title": "Activación Directa ante Administrador tras Auto Autorizado",
            "legal_basis": "CPCNL Artículo 64",
            "operational_advantage": "Permite destrabar acceso electrónico si el juzgado dictó el acuerdo pero omitió habilitar el módulo.",
        },
        {
            "id": "CAP-06",
            "title": "Exhortos y Despachos Electrónicos con Expediente Independiente",
            "legal_basis": "CPCNL Arts. 79-80 y Acuerdos 5-II/2013, 2-II/2017",
            "operational_advantage": "Tramita y devuelve exhortos inter-distritales sin traslados físicos.",
        },
        {
            "id": "CAP-07",
            "title": "Remisión Electrónica de Incompetencias Mercantiles",
            "legal_basis": "Acuerdos Generales Conjuntos 3-II/2014 y 7-II/2021",
            "operational_advantage": "Envío electrónico de constancias e incompetencias entre órganos del PJENL.",
        },
        {
            "id": "CAP-08",
            "title": "Copias Certificadas en Formato Electrónico",
            "legal_basis": "Acuerdo General Conjunto 3-II/2015",
            "operational_advantage": "Emisión y descarga digital de constancias certificadas sin esperas de mostrador.",
        },
        {
            "id": "CAP-09",
            "title": "Carpeta Digital Penal, Ejecución, Adolescentes y Juzgado Laboral",
            "legal_basis": "Acuerdos 15/2011, 5/2018 y 16/2022",
            "operational_advantage": "Extiende sustanciación digital a causas penales acusatorias y litigio laboral estatal.",
        },
        {
            "id": "CAP-10",
            "title": "Medios Electrónicos Integrales, UMC, Citas UAPA y Cabinas Virtuales",
            "legal_basis": "Acuerdo General Conjunto 1-II/2024, Reglamento UMC y MASC/IMASC",
            "operational_advantage": "Agenda de actuarios UMC en línea, comparecencias remotas y citas UAPA para billetes de depósito.",
        },
    ),
    "training_and_support": {
        "tutorials_portal": "https://www.pjenl.gob.mx/Instituto/Tutoriales/",
        "sicavi_campus": "https://www.pjenl.gob.mx/Instituto/SiCavi/",
        "masc_clarification": "En normativa oficial PJENL no figura un módulo llamado 'Dialoga'; la mediación opera mediante el IMASC (Reglamento de la Ley MASC + Acuerdo 14/2017).",
        "helpdesk_email": "cst@pjenl.gob.mx",
        "helpdesk_phone": "(81) 2020-7751",
    },
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
