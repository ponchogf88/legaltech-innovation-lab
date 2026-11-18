"""Specialized legal continuing education, diploma tracking, and course reminder engine."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from .security import assert_synthetic_and_safe

COURSE_STATUSES: tuple[str, ...] = (
    "POR_INICIAR",
    "EN_CURSO",
    "EVALUACION_PENDIENTE",
    "CERTIFICADO",
)

COURSE_KINDS: tuple[str, ...] = (
    "DIPLOMADO",
    "CURSO_ESPECIALIZADO",
    "CERTIFICACION",
    "SEMINARIO",
)

LEGAL_PRACTICE_AREAS: tuple[str, ...] = (
    "Mercantil y Bancario",
    "Amparo y Constitucional",
    "Civil y Contratos",
    "Litigio Oral y Forense",
    "Derecho Procesal y Tecnología Legal",
)


class AcademyValidationError(ValueError):
    """Raised when a legal continuing-education course record fails schema validation."""


@dataclass
class LegalCourse:
    """Represents a continuing legal education course, diploma, or certification."""

    id: str
    title: str
    institution: str
    practice_area: str
    kind: str
    start_date: str
    end_date: str
    next_milestone_date: str
    next_milestone_label: str
    status: str
    credit_hours: int
    progress_pct: int
    certificate_folio: str | None = None
    linked_council_agent: str = "Ulpiano"

    def to_dict(self) -> dict[str, Any]:
        """Serialize course record to a plain JSON-friendly dictionary."""
        return asdict(self)


@dataclass
class CourseReminder:
    """Upcoming start date, session, or certification deadline reminder for a legal course."""

    course_id: str
    course_title: str
    institution: str
    milestone_date: str
    milestone_label: str
    days_until: int
    urgency: str
    action_prompt: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize reminder record to a plain JSON-friendly dictionary."""
        return asdict(self)


def _require_non_empty_str(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise AcademyValidationError(f"Field '{field}' is required and must be a non-empty string.")
    return value.strip()


def _parse_iso_date(raw_date: str, field: str) -> date:
    try:
        return date.fromisoformat(raw_date)
    except ValueError as exc:
        raise AcademyValidationError(
            f"Field '{field}' must be an ISO-8601 date (YYYY-MM-DD), got {raw_date!r}."
        ) from exc


def validate_legal_course(raw: dict[str, Any]) -> LegalCourse:
    """Validate synthetic safety and structural domain contract for a LegalCourse."""
    if not isinstance(raw, dict):
        raise AcademyValidationError("Course payload must be a JSON object.")

    assert_synthetic_and_safe(raw)

    course_id = _require_non_empty_str(raw, "id")
    title = _require_non_empty_str(raw, "title")
    institution = _require_non_empty_str(raw, "institution")
    practice_area = _require_non_empty_str(raw, "practice_area")
    kind = _require_non_empty_str(raw, "kind")
    start_date_str = _require_non_empty_str(raw, "start_date")
    end_date_str = _require_non_empty_str(raw, "end_date")
    milestone_date_str = _require_non_empty_str(raw, "next_milestone_date")
    milestone_label = _require_non_empty_str(raw, "next_milestone_label")
    status = _require_non_empty_str(raw, "status")

    if practice_area not in LEGAL_PRACTICE_AREAS:
        raise AcademyValidationError(
            f"Invalid practice_area {practice_area!r}; allowed: {LEGAL_PRACTICE_AREAS}"
        )
    if kind not in COURSE_KINDS:
        raise AcademyValidationError(f"Invalid kind {kind!r}; allowed: {COURSE_KINDS}")
    if status not in COURSE_STATUSES:
        raise AcademyValidationError(f"Invalid status {status!r}; allowed: {COURSE_STATUSES}")

    start_dt = _parse_iso_date(start_date_str, "start_date")
    end_dt = _parse_iso_date(end_date_str, "end_date")
    _parse_iso_date(milestone_date_str, "next_milestone_date")
    if end_dt < start_dt:
        raise AcademyValidationError("end_date cannot precede start_date.")

    credit_hours = raw.get("credit_hours")
    if not isinstance(credit_hours, int) or isinstance(credit_hours, bool) or credit_hours <= 0:
        raise AcademyValidationError("credit_hours must be a positive integer.")

    progress_pct = raw.get("progress_pct")
    if (
        not isinstance(progress_pct, int)
        or isinstance(progress_pct, bool)
        or not (0 <= progress_pct <= 100)
    ):
        raise AcademyValidationError("progress_pct must be an integer between 0 and 100.")

    certificate_folio = raw.get("certificate_folio")
    if certificate_folio is not None and (
        not isinstance(certificate_folio, str) or not certificate_folio.strip()
    ):
        raise AcademyValidationError("certificate_folio must be null or a non-empty string.")
    if status == "CERTIFICADO" and not certificate_folio:
        raise AcademyValidationError("CERTIFICADO courses require a non-empty certificate_folio.")

    linked_agent = str(raw.get("linked_council_agent") or "Ulpiano").strip()

    return LegalCourse(
        id=course_id,
        title=title,
        institution=institution,
        practice_area=practice_area,
        kind=kind,
        start_date=start_date_str,
        end_date=end_date_str,
        next_milestone_date=milestone_date_str,
        next_milestone_label=milestone_label,
        status=status,
        credit_hours=credit_hours,
        progress_pct=progress_pct,
        certificate_folio=certificate_folio.strip() if isinstance(certificate_folio, str) else None,
        linked_council_agent=linked_agent,
    )


def _classify_urgency(days_until: int) -> str:
    if days_until <= 3:
        return "high"
    if days_until <= 7:
        return "medium"
    return "low"


def _build_action_prompt(course: LegalCourse, days_until: int) -> str:
    if days_until < 0:
        return (
            f"Hito vencido hace {abs(days_until)} día(s): confirmar ingreso o actualizar estatus de "
            f"'{course.title}' ({course.institution})."
        )
    if days_until == 0:
        return f"¡Hoy! {course.next_milestone_label} en '{course.title}' ({course.institution})."
    if course.status == "POR_INICIAR":
        return (
            f"Inicia en {days_until} día(s) ({course.next_milestone_date}): "
            f"preparar acceso para '{course.title}' con apoyo de {course.linked_council_agent}."
        )
    return (
        f"En {days_until} día(s) ({course.next_milestone_date}): "
        f"{course.next_milestone_label} para avanzar hacia tu certificado legal."
    )


def compute_course_reminders(
    courses: Sequence[LegalCourse],
    reference_date: date | None = None,
) -> list[CourseReminder]:
    """Compute sorted proactive reminders for all active or upcoming (non-certified) courses."""
    today = reference_date if reference_date is not None else date.today()
    reminders: list[CourseReminder] = []

    for course in courses:
        if course.status == "CERTIFICADO":
            continue
        milestone_dt = _parse_iso_date(course.next_milestone_date, "next_milestone_date")
        days_until = (milestone_dt - today).days
        reminders.append(
            CourseReminder(
                course_id=course.id,
                course_title=course.title,
                institution=course.institution,
                milestone_date=course.next_milestone_date,
                milestone_label=course.next_milestone_label,
                days_until=days_until,
                urgency=_classify_urgency(days_until),
                action_prompt=_build_action_prompt(course, days_until),
            )
        )

    reminders.sort(key=lambda r: (r.days_until, r.course_id))
    return reminders


def summarize_lawyer_academy(
    courses: Sequence[LegalCourse],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Aggregate continuing legal education metrics, earned certificates, and upcoming reminders."""
    reminders = compute_course_reminders(courses, reference_date=reference_date)
    reminder_by_id = {r.course_id: r for r in reminders}

    starting_soon_count = sum(
        1
        for course in courses
        if course.status == "POR_INICIAR"
        and course.id in reminder_by_id
        and reminder_by_id[course.id].days_until <= 7
    )
    in_progress_count = sum(
        1 for course in courses if course.status in {"EN_CURSO", "EVALUACION_PENDIENTE"}
    )
    certificates_earned_count = sum(1 for course in courses if course.status == "CERTIFICADO")
    completed_credit_hours = sum(
        course.credit_hours for course in courses if course.status == "CERTIFICADO"
    )
    total_enrolled_hours = sum(course.credit_hours for course in courses)

    return {
        "specialization": "Práctica Legal Exclusiva (Cero ruido generalista)",
        "total_courses": len(courses),
        "starting_soon_count": starting_soon_count,
        "in_progress_count": in_progress_count,
        "certificates_earned_count": certificates_earned_count,
        "completed_credit_hours": completed_credit_hours,
        "total_enrolled_hours": total_enrolled_hours,
        "reminders": [r.to_dict() for r in reminders],
    }
