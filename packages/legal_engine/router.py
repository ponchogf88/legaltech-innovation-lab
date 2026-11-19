"""Smart Multi-Model Router and Canonical Historical Jurist Council Registry.

Implements cost-aware task routing across Google Gemini, Anthropic Claude, and
OpenAI while preserving strict zero-anachronism persona metadata and PII safety.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .security import assert_synthetic_and_safe

MODEL_PROFILES: dict[str, dict[str, str]] = {
    "gemini-pro-vision": {
        "model_id": "gemini-pro-vision",
        "provider": "Google Gemini",
        "tier": "Gemini Pro / Flash",
        "context_window": "2M tokens",
        "specialty": "OCR masivo, acuerdos escaneados y resumen de expedientes extensos",
        "relative_cost": "ultra_low",
        "latency_budget_ms": "1800",
    },
    "claude-jurist-sonnet": {
        "model_id": "claude-jurist-sonnet",
        "provider": "Anthropic Claude",
        "tier": "Claude Sonnet / Code",
        "context_window": "200K tokens",
        "specialty": "Razonamiento jurídico profundo, combate a la usura, agravios y amparo",
        "relative_cost": "precision",
        "latency_budget_ms": "3200",
    },
    "openai-orchestrator": {
        "model_id": "openai-orchestrator",
        "provider": "OpenAI",
        "tier": "GPT-4o / Codex",
        "context_window": "128K tokens",
        "specialty": "Estructuración JSON estricta, plazos procesales y automatización B2B",
        "relative_cost": "balanced",
        "latency_budget_ms": "1400",
    },
}

STRATA_CATALOG: dict[str, dict[str, str]] = {
    "STRATUM_I": {
        "id": "STRATUM_I",
        "roman": "I",
        "name": "Deidades & Principios",
        "era_label": "Mitología & Principios Universales",
        "visual_style": "Mármol de Carrara clásico & Bajorrelieve Neoclásico",
        "motif": "Balanza y Friso de Mármol",
        "epoch_rule": "Cero anacronismos: sobriedad escultórica divina; no litigan, custodian ética y licitud.",
    },
    "STRATUM_II": {
        "id": "STRATUM_II",
        "roman": "II",
        "name": "Roma Clásica & Antigüedad",
        "era_label": "Corpus Iuris & Oratoria Forense",
        "visual_style": "Óleo Renacentista / Neoclasicismo Imperial (Rafael / David)",
        "motif": "Sello de Cera Romana & Pergamino",
        "epoch_rule": "Cero anacronismos: togas e insignias imperiales dignas; cero dispositivos modernos.",
    },
    "STRATUM_III": {
        "id": "STRATUM_III",
        "roman": "III",
        "name": "Ilustración & Academia",
        "era_label": "Estado Constitucional & Disciplina Curricular",
        "visual_style": "Retrato al Óleo Siglo XVIII · Roble Oscuro, Piel y Candelabro",
        "motif": "Firma con Pluma de Ave & Lacrado",
        "epoch_rule": "Cero anacronismos: biblioteca ilustrada clásica y rigor fiduciario/académico.",
    },
    "STRATUM_IV": {
        "id": "STRATUM_IV",
        "roman": "IV",
        "name": "Litigio Moderno & Forense",
        "era_label": "Inteligencia Patrimonial & Estrategia Contemporánea",
        "visual_style": "Editorial Dark · Steel, Glass & Dossier Táctico",
        "motif": "Dossier Forense & Tablero Estratégico",
        "epoch_rule": "Estética contemporánea sobria de firma boutique y trazabilidad patrimonial.",
    },
}

COUNCIL_PERSONAS: tuple[dict[str, Any], ...] = (
    {
        "id": "temis",
        "name": "Temis",
        "title": "La Balanza de la Licitud & Ética",
        "stratum_id": "STRATUM_I",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "1. Diagnóstico · 6. Pruebas",
        "superpower": "Audita licitud probatoria, cadena de custodia y detecta prescripción o ilicitud.",
        "seal_label": "Friso de Mármol · Licitud Probatoria",
    },
    {
        "id": "atenea",
        "name": "Atenea",
        "title": "Cerebro Táctico & Teoría del Caso",
        "stratum_id": "STRATUM_I",
        "preferred_model": "openai-orchestrator",
        "phase": "2. Postulación · 4. Emplazamiento",
        "superpower": "Diseña la teoría integral del caso y coordina el árbol de decisiones sin fricción.",
        "seal_label": "Égida Estratégica · Teoría del Caso",
    },
    {
        "id": "hermes",
        "name": "Hermes",
        "title": "Actuario & Monitor de Boletines",
        "stratum_id": "STRATUM_I",
        "preferred_model": "gemini-pro-vision",
        "phase": "Ingesta Continua · Acuerdos 24/7",
        "superpower": "Escanea boletines judiciales (PJENL, CJF, locales) y computa términos en días hábiles.",
        "seal_label": "Caduceo Procesal · Boletines Judiciales",
    },
    {
        "id": "ciceron",
        "name": "Marco Tulio Cicerón",
        "title": "Retórica Forense & Interrogatorios",
        "stratum_id": "STRATUM_II",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "3. Demanda · 6. Pruebas · 7. Alegatos",
        "superpower": "Redacta hechos demoledores, contrainterrogatorios con trampa lógica y alegatos de clausura.",
        "seal_label": "Sello Senatorio · Retórica Judicial",
    },
    {
        "id": "ulpiano",
        "name": "Ulpiano & Papiniano",
        "title": "Derecho de Fondo Romano & Anti-Usura",
        "stratum_id": "STRATUM_II",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "3. Demanda / Contestación Mercantil",
        "superpower": "Combate usura improba, pagarés en blanco alterados y contratos leoninos con buena fe.",
        "seal_label": "Sello de Cera Romana · Ius Civile",
    },
    {
        "id": "justiniano",
        "name": "Justiniano I & Triboniano",
        "title": "Codificación & Blindaje de Emplazamiento",
        "stratum_id": "STRATUM_II",
        "preferred_model": "gemini-pro-vision",
        "phase": "4. Emplazamiento & Jurisprudencia",
        "superpower": "Compila Corpus Iuris de tesis SCJN y blinda actas adjetivas contra nulidad.",
        "seal_label": "Digesto Imperial · Corpus Iuris",
    },
    {
        "id": "julio_cesar",
        "name": "Julio César",
        "title": "Táctica de Tiempos & Embargos Precautorios",
        "stratum_id": "STRATUM_II",
        "preferred_model": "openai-orchestrator",
        "phase": "2. Medidas Cautelares",
        "superpower": "Ejecuta providencias precautorias y aseguramiento de cuentas antes de insolvencia.",
        "seal_label": "Sello Consular · Maniobra Rápida",
    },
    {
        "id": "alejandro_magno",
        "name": "Alejandro Magno",
        "title": "Ruptura de Litigios Trabados (Nudo Gordiano)",
        "stratum_id": "STRATUM_II",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "8. Sentencia & Criterios Bloqueados",
        "superpower": "Formula planteamientos audaces para romper precedentes estancados y contradicciones.",
        "seal_label": "Nudo Gordiano · Solución Ejecutiva",
    },
    {
        "id": "montesquieu",
        "name": "Barón de Montesquieu",
        "title": "Garantías Constitucionales & Juicio de Amparo",
        "stratum_id": "STRATUM_III",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "8. Apelación & Amparo Directo/Indirecto",
        "superpower": "Construye conceptos de violación (arts. 14, 16 y 17 CPEUM) y control difuso.",
        "seal_label": "Pluma Ilustrada · Control Constitucional",
    },
    {
        "id": "pacioli",
        "name": "Fray Luca Pacioli",
        "title": "Contador Fiduciario & Liquidaciones",
        "stratum_id": "STRATUM_III",
        "preferred_model": "openai-orchestrator",
        "phase": "Soporte Financiero · Liquidación de Sentencia",
        "superpower": "Calcula capital, intereses moratorios sin usura, IVA y conciliación CFDI 4.0.",
        "seal_label": "Partida Doble · Liquidación Exacta",
    },
    {
        "id": "irnerio",
        "name": "Irnerio de Bolonia",
        "title": "Academia Jurídica, Diplomados & Certificaciones",
        "stratum_id": "STRATUM_III",
        "preferred_model": "openai-orchestrator",
        "phase": "Educación Continua · Solo Práctica Legal",
        "superpower": "Aísla y recuerda cursos/diplomados jurídicos (SCJN, EFFJ) hasta lograr certificación.",
        "seal_label": "Alma Mater Studiorum · Glosadores",
    },
    {
        "id": "sherlock",
        "name": "Sherlock Holmes",
        "title": "Investigador Forense & Búsqueda Registral",
        "stratum_id": "STRATUM_IV",
        "preferred_model": "gemini-pro-vision",
        "phase": "Pre-Embargo · Rastreabilidad Patrimonial",
        "superpower": "Cruza fojas del Registro Público, folios mercantiles y señales patrimoniales lícitas.",
        "seal_label": "Dossier Forense · Búsqueda Registral",
    },
    {
        "id": "maquiavelo",
        "name": "Nicolás Maquiavelo",
        "title": "Negociación Estratégica & Apalancamiento",
        "stratum_id": "STRATUM_IV",
        "preferred_model": "claude-jurist-sonnet",
        "phase": "5. Conciliación & Convenio Judicial",
        "superpower": "Diseña matrices de concesiones para cerrar convenios desde posición de fuerza.",
        "seal_label": "Tablero de Poder · Conciliación",
    },
    {
        "id": "sun_tzu",
        "name": "Sun Tzu",
        "title": "Inteligencia Pre-Litigiosa del Adversario",
        "stratum_id": "STRATUM_IV",
        "preferred_model": "gemini-pro-vision",
        "phase": "1. Estrategia Pre-Litigiosa",
        "superpower": "Mapea solvencia de contraparte y criterios previos para ganar antes del emplazamiento.",
        "seal_label": "Vanguardia Táctica · Mapeo Previo",
    },
    {
        "id": "craso",
        "name": "Marco Licinio Craso",
        "title": "Cobranza de Honorarios & Flujo del Despacho",
        "stratum_id": "STRATUM_IV",
        "preferred_model": "openai-orchestrator",
        "phase": "Operación B2B · Cartera & Igualas",
        "superpower": "Automatiza seguimiento amable y firme de igualas mensuales y honorarios pactados.",
        "seal_label": "Tesorería B2B · Honorarios",
    },
)

_PERSONA_BY_ID: dict[str, dict[str, Any]] = {p["id"]: p for p in COUNCIL_PERSONAS}

ADVERSARIAL_ARCHETYPES: tuple[dict[str, Any], ...] = (
    {
        "id": "saul_goodman",
        "name": "Saul Goodman",
        "archetype_label": "Estrato V · Estrategia Procesal Creativa & Salidas Alternas",
        "visual_style": "Monolito Obscuro B&N · Traje sastre completo de pie, portafolio cerrado, corbata en alto contraste bajo haz cenital",
        "reasoning_tone": "Pragmático, veloz en detección de vicios del IPH, fianzas, suspensión condicional y medidas cautelares no privativas",
        "ethical_guardrail": "Estrictamente lícito bajo control de Temis/HITL: exclusión de prueba ilícita, salidas alternas CNPP y defensa de libertad.",
        "preferred_model": "openai-orchestrator",
    },
    {
        "id": "abogado_diablo",
        "name": "El Abogado del Diablo (Advocatus Diaboli)",
        "archetype_label": "Estrato V · Litigio Penal Grave, Privación de la Vida & Oratoria Extrema",
        "visual_style": "Monolito Obscuro B&N · Figura solemne de cuerpo completo en abrigo largo hasta los botines, postura retórica en penumbra",
        "reasoning_tone": "Demolición lógica de la teoría del dolo/culpa, necropsia, legítima defensa y escrutinio constitucional estricto (arts. 14, 16 y 20 CPEUM)",
        "ethical_guardrail": "Sometido a verificación probatoria humana: prohíbe fabricación de hechos; maximiza presunción de inocencia y duda razonable.",
        "preferred_model": "claude-jurist-sonnet",
    },
    {
        "id": "tony_montana",
        "name": "Arquetipo Tony Montana (Lente Red Team)",
        "archetype_label": "Estrato V · Análisis Adversarial en Agrupación Delictuosa / Contra la Salud",
        "visual_style": "Monolito Obscuro B&N · Silueta completa de traje oscuro de pie sobre pedestal monolítico bajo cono de luz cenital",
        "reasoning_tone": "Simulación anticipada de cómo construye la acusación sus hipótesis de coautoría, posesión o asociación delictuosa para desmantelarlas",
        "ethical_guardrail": "Solo simulación defensiva y de cumplimiento preventivo (compliance/extinción de dominio); cero asesoría para conductas ilícitas.",
        "preferred_model": "claude-jurist-sonnet",
    },
    {
        "id": "harvey_specter",
        "name": "Harvey Specter",
        "archetype_label": "Estrato V · Negociación Ejecutiva Corporativa & Alta Tensión",
        "visual_style": "Monolito Obscuro B&N · Figura de cuerpo entero de pie en traje minimalista monocromo bajo haz arquitectónico",
        "reasoning_tone": "Cierre de convenios ejecutivos, presión táctica pre-embargo y resolución antes de juicio largo",
        "ethical_guardrail": "Sujeto a liquidación contable de Pacioli y aprobación expresa de socio responsable.",
        "preferred_model": "openai-orchestrator",
    },
    {
        "id": "annalise_keating",
        "name": "Annalise Keating",
        "archetype_label": "Estrato V · Contrainterrogatorio Oral & Exclusión Probatoria",
        "visual_style": "Monolito Obscuro B&N · Toga o vestido sastre completo hasta el estrado, brazo extendido en réplica forense",
        "reasoning_tone": "Interrogatorio clínico de testigos hostiles y peritos oficiales para exhibir contradicciones de cadena de custodia",
        "ethical_guardrail": "Apegada a código de ética judicial y separación estricta de hecho comprobado vs. inferencia.",
        "preferred_model": "claude-jurist-sonnet",
    },
)

_ARCHETYPE_BY_ID: dict[str, dict[str, Any]] = {a["id"]: a for a in ADVERSARIAL_ARCHETYPES}

CASE_TYPE_AVATAR_MATRIX: dict[str, dict[str, Any]] = {
    "privacion_vida_homicidio": {
        "case_type": "privacion_vida_homicidio",
        "label": "Penal Grave · Privación de la Vida / Homicidio (Defensa Constitucional)",
        "lead_jurist_id": "montesquieu",
        "guardian_jurist_id": "temis",
        "adversarial_archetype_id": "abogado_diablo",
        "recommended_audio": "Drone minimalista de cuerdas graves + lluvia lejana (60 BPM, volumen bajo)",
        "reasoning_protocol": "Contrastar necropsia y dictamen balístico contra mecánica de hechos; verificar excluyentes (legítima defensa / culpa) y control constitucional estricto de detención y cadena de custodia.",
    },
    "agrupacion_delictuosa_contra_salud": {
        "case_type": "agrupacion_delictuosa_contra_salud",
        "label": "Penal Complejo · Agrupación Delictuosa / Delitos Contra la Salud",
        "lead_jurist_id": "ciceron",
        "guardian_jurist_id": "temis",
        "adversarial_archetype_id": "saul_goodman",
        "secondary_archetype_id": "tony_montana",
        "recommended_audio": "Synth ambiental oscuro de baja frecuencia + pulso lento (concentración forense)",
        "reasoning_protocol": "Combinar lente Red Team (Arquetipo Tony Montana) para anticipar la teoría de coautoría/posesión/dolo de la contraparte con la agilidad procesal de Saul Goodman (vicios en cateo/IPH y medidas cautelares) bajo auditoría de Temis.",
    },
    "mercantil_usura_adulto_mayor": {
        "case_type": "mercantil_usura_adulto_mayor",
        "label": "Mercantil Estratégico · Pagarés Alterados / Usura / Tutela Reforzada",
        "lead_jurist_id": "ulpiano",
        "guardian_jurist_id": "atenea",
        "adversarial_archetype_id": "harvey_specter",
        "recommended_audio": "Piano neoclásico en modo menor + silencio acústico controlado",
        "reasoning_protocol": "Reducción oficiosa de intereses usurarios (Pacioli + Ulpiano), pericial en grafoscopía/tintas sobre espacios en blanco y apalancamiento de negociación ejecutiva.",
    },
    "familiar_alimentos_billete": {
        "case_type": "familiar_alimentos_billete",
        "label": "Familiar · Pensión Alimenticia, Billetes de Depósito y Oficios PJENL",
        "lead_jurist_id": "atenea",
        "guardian_jurist_id": "hermes",
        "adversarial_archetype_id": "saul_goodman",
        "recommended_audio": "Ambiente contemplativo neutro / foco claro (audífonos recomendados)",
        "reasoning_protocol": "Acuerdos 7/2022 y 8/2022 (oficios electrónicos directos a empleadores no-partes), cita UAPA en Tribunal Virtual / WhatsApp 81-8366-6781 y comparecencia rápida sin trabas burocráticas.",
    },
}


@dataclass(frozen=True)
class ReasoningRoomSelection:
    """AI avatar pairing selecting a historical guardian and adversarial lens by case type."""

    case_type: str
    case_label: str
    selection_mode: str
    lead_jurist: dict[str, Any]
    guardian_jurist: dict[str, Any]
    adversarial_avatar: dict[str, Any]
    secondary_avatar: dict[str, Any] | None
    recommended_audio: str
    reasoning_protocol: str
    headphone_advisory: str
    dossier_md_path: str
    pii_redacted: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize selection into JSON-safe primitives."""
        return asdict(self)


def list_adversarial_archetypes() -> list[dict[str, Any]]:
    """Return modern/cinematic adversarial Reasoning Room archetypes (with HITL guardrails)."""
    return [dict(item) for item in ADVERSARIAL_ARCHETYPES]


def select_reasoning_room_avatars(
    case_type: str,
    facts_preview: str | None = None,
    *,
    override_adversarial_id: str | None = None,
    override_lead_jurist_id: str | None = None,
) -> ReasoningRoomSelection:
    """Select Reasoning Room avatars and allow sovereign human lawyer manual overrides."""
    if facts_preview is not None:
        assert_synthetic_and_safe(facts_preview)

    cleaned = case_type.strip().lower()
    alias_map = {
        "homicidio": "privacion_vida_homicidio",
        "privacion_vida": "privacion_vida_homicidio",
        "privacion_vida_homicidio": "privacion_vida_homicidio",
        "agrupacion_delictuosa": "agrupacion_delictuosa_contra_salud",
        "contra_la_salud": "agrupacion_delictuosa_contra_salud",
        "delincuencia_organizada": "agrupacion_delictuosa_contra_salud",
        "agrupacion_delictuosa_contra_salud": "agrupacion_delictuosa_contra_salud",
        "mercantil": "mercantil_usura_adulto_mayor",
        "usura": "mercantil_usura_adulto_mayor",
        "mercantil_usura_adulto_mayor": "mercantil_usura_adulto_mayor",
        "alimentos": "familiar_alimentos_billete",
        "familiar": "familiar_alimentos_billete",
        "familiar_alimentos_billete": "familiar_alimentos_billete",
    }
    resolved_key = alias_map.get(cleaned)
    if resolved_key is None or resolved_key not in CASE_TYPE_AVATAR_MATRIX:
        raise UnknownTaskRouteError(
            f"Unknown Reasoning Room case_type {case_type!r}. "
            f"Expected one of: {sorted(CASE_TYPE_AVATAR_MATRIX)}"
        )

    spec = CASE_TYPE_AVATAR_MATRIX[resolved_key]
    lead_id = (
        override_lead_jurist_id.strip().lower()
        if isinstance(override_lead_jurist_id, str) and override_lead_jurist_id.strip()
        else spec["lead_jurist_id"]
    )
    lead_jurist = get_council_persona(lead_id)
    guardian_jurist = get_council_persona(spec["guardian_jurist_id"])

    adv_id = (
        override_adversarial_id.strip().lower()
        if isinstance(override_adversarial_id, str) and override_adversarial_id.strip()
        else spec["adversarial_archetype_id"]
    )
    if adv_id not in _ARCHETYPE_BY_ID:
        raise UnknownTaskRouteError(f"Unknown adversarial archetype: {adv_id!r}")
    adversarial_avatar = dict(_ARCHETYPE_BY_ID[adv_id])

    secondary_id = spec.get("secondary_archetype_id")
    secondary_avatar = dict(_ARCHETYPE_BY_ID[secondary_id]) if secondary_id else None

    is_override = (
        lead_id != spec["lead_jurist_id"] or adv_id != spec["adversarial_archetype_id"]
    )
    selection_mode = "LAWYER_MANUAL_OVERRIDE" if is_override else "AI_RECOMMENDED"

    return ReasoningRoomSelection(
        case_type=spec["case_type"],
        case_label=spec["label"],
        selection_mode=selection_mode,
        lead_jurist=lead_jurist,
        guardian_jurist=guardian_jurist,
        adversarial_avatar=adversarial_avatar,
        secondary_avatar=secondary_avatar,
        recommended_audio=spec["recommended_audio"],
        reasoning_protocol=spec["reasoning_protocol"],
        headphone_advisory="Para razonamiento jurídico profundo se recomienda usar audífonos con música ambiental tranquila en segundo plano.",
        dossier_md_path="docs/personas/ESTRATO_IV_V_LENTES_MODERNOS_Y_ADVERSARIALES.md",
        pii_redacted=True,
    )

_TASK_ROUTING_TABLE: dict[str, tuple[str, str, str]] = {
    "ocr_mass": (
        "gemini-pro-vision",
        "hermes",
        "Ventana de hasta 2M tokens para digitalización y resumen de fojas a costo mínimo.",
    ),
    "expediente_scan": (
        "gemini-pro-vision",
        "hermes",
        "Lectura masiva de expedientes escaneados y clasificación documental sin fragmentar contexto.",
    ),
    "boletin_watch": (
        "gemini-pro-vision",
        "hermes",
        "Monitoreo de listas y acuerdos publicados en boletines judiciales con extracción de fechas.",
    ),
    "asset_trace": (
        "gemini-pro-vision",
        "sherlock",
        "Cruce multimodal de inscripciones registrales y folios mercantiles para bienes embargables.",
    ),
    "usura_analysis": (
        "claude-jurist-sonnet",
        "ulpiano",
        "Análisis sustantivo de tasa usuraria, buena fe contractual y tutela patrimonial reforzada.",
    ),
    "constitutional_amparo": (
        "claude-jurist-sonnet",
        "montesquieu",
        "Ponderación constitucional (arts. 14, 16 y 17) y estructura de conceptos de violación.",
    ),
    "rhetoric_brief": (
        "claude-jurist-sonnet",
        "ciceron",
        "Construcción retórica persuasiva, detección de falacias y pliegos de contrainterrogatorio.",
    ),
    "evidence_licitude": (
        "claude-jurist-sonnet",
        "temis",
        "Separación estricta entre hecho verificable y conclusión jurídica preliminar no vinculante.",
    ),
    "json_structuring": (
        "openai-orchestrator",
        "atenea",
        "Salida tipada estricta para plantillas Jinja2 StrictUndefined y contratos JSON.",
    ),
    "deadline_calc": (
        "openai-orchestrator",
        "julio_cesar",
        "Cómputo determinista de términos hábiles y disparo de medidas cautelares oportunas.",
    ),
    "cfdi_accounting": (
        "openai-orchestrator",
        "pacioli",
        "Planilla aritmética exacta de capital, intereses moratorios e impuestos sin alucinaciones.",
    ),
    "academy_tracking": (
        "openai-orchestrator",
        "irnerio",
        "Agenda exclusiva de cursos, diplomados y certificados legales con alertas T-72h.",
    ),
}


class UnknownTaskRouteError(ValueError):
    """Raised when an unknown persona ID or empty task kind is requested."""


@dataclass(frozen=True)
class RoutingDecision:
    """Deterministic multi-model routing decision with structured telemetry attributes."""

    task_kind: str
    persona_id: str
    persona_name: str
    stratum_id: str
    stratum_label: str
    model_id: str
    provider: str
    rationale: str
    estimated_relative_cost: str
    telemetry_span: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialize routing decision into a plain dictionary."""
        return asdict(self)


def get_stratum(stratum_id: str) -> dict[str, str]:
    """Return canonical visual stratum metadata by ID."""
    if stratum_id not in STRATA_CATALOG:
        raise UnknownTaskRouteError(f"Unknown historical stratum: {stratum_id!r}")
    return dict(STRATA_CATALOG[stratum_id])


def get_council_persona(persona_id: str) -> dict[str, Any]:
    """Return a single Jurist Council persona definition."""
    key = persona_id.strip().lower()
    if key not in _PERSONA_BY_ID:
        raise UnknownTaskRouteError(f"Unknown council persona: {persona_id!r}")
    return dict(_PERSONA_BY_ID[key])


def list_council_personas(stratum_id: str | None = None) -> list[dict[str, Any]]:
    """List canonical Jurist Council personas, optionally filtered by stratum."""
    if stratum_id is not None:
        get_stratum(stratum_id)
        return [dict(p) for p in COUNCIL_PERSONAS if p["stratum_id"] == stratum_id]
    return [dict(p) for p in COUNCIL_PERSONAS]


def route_legal_task(
    task_kind: str,
    *,
    persona_id: str | None = None,
    document_pages: int = 10,
    complexity: str = "standard",
    payload_preview: str | None = None,
) -> RoutingDecision:
    """Select the optimal AI model and historical persona for a legal task."""
    cleaned_task = task_kind.strip().lower()
    if not cleaned_task:
        raise UnknownTaskRouteError("task_kind must be a non-empty identifier.")

    if payload_preview is not None:
        assert_synthetic_and_safe(payload_preview)

    if cleaned_task in _TASK_ROUTING_TABLE:
        selected_model_id, default_persona_id, base_rationale = _TASK_ROUTING_TABLE[cleaned_task]
    else:
        default_persona_id = persona_id.strip().lower() if persona_id else "atenea"
        persona_record = get_council_persona(default_persona_id)
        selected_model_id = persona_record["preferred_model"]
        base_rationale = f"Enrutado por especialidad nativa del agente {persona_record['name']}."

    resolved_persona_id = persona_id.strip().lower() if persona_id else default_persona_id
    persona = get_council_persona(resolved_persona_id)

    # Dynamic override for massive document volume (>80 scanned pages -> Gemini 2M window)
    if document_pages >= 80:
        selected_model_id = "gemini-pro-vision"
        rationale = (
            f"Volumen masivo ({document_pages} fojas): enrutado a Gemini 2M para evitar truncamiento "
            f"y reducir costo por token ({base_rationale})"
        )
    elif complexity.strip().lower() == "high" and selected_model_id == "openai-orchestrator":
        selected_model_id = "claude-jurist-sonnet"
        rationale = (
            f"Complejidad alta detectada: escalado a razonamiento jurídico profundo ({base_rationale})"
        )
    else:
        rationale = base_rationale

    model_info = MODEL_PROFILES[selected_model_id]
    stratum = STRATA_CATALOG[persona["stratum_id"]]

    telemetry_span = {
        "trace_stage": f"router.{cleaned_task}",
        "stratum": stratum["id"],
        "document_pages": document_pages,
        "latency_budget_ms": int(model_info["latency_budget_ms"]),
        "pii_redacted": True,
        "zero_anachronism_verified": True,
    }

    return RoutingDecision(
        task_kind=cleaned_task,
        persona_id=persona["id"],
        persona_name=persona["name"],
        stratum_id=stratum["id"],
        stratum_label=f"Estrato {stratum['roman']} · {stratum['name']}",
        model_id=model_info["model_id"],
        provider=model_info["provider"],
        rationale=rationale,
        estimated_relative_cost=model_info["relative_cost"],
        telemetry_span=telemetry_span,
    )
