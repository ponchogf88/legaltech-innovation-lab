"""Synthetic legal deadline rules and upcoming schedule calculations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .models import Matter

DEFAULT_DEADLINE_RULES: dict[str, list[dict[str, Any]]] = {
    "solicitud": [
        {"title": "Revisión humana de solicitud", "offset_days": 2, "priority": "high"},
        {"title": "Presentación ante autoridad", "offset_days": 5, "priority": "high"},
        {"title": "Seguimiento de acuse sintético", "offset_days": 10, "priority": "medium"},
    ],
    "mercantil": [
        {"title": "Validación documental mercantil", "offset_days": 3, "priority": "high"},
        {"title": "Término de promoción inicial", "offset_days": 8, "priority": "high"},
        {"title": "Verificación de acuerdo / acuse", "offset_days": 15, "priority": "medium"},
    ],
    "fiscal": [
        {"title": "Revisión de expediente fiscal", "offset_days": 3, "priority": "high"},
        {"title": "Presentación programada", "offset_days": 10, "priority": "high"},
        {"title": "Seguimiento de resolución", "offset_days": 30, "priority": "medium"},
    ],
    "default": [
        {"title": "Revisión humana obligatoria", "offset_days": 2, "priority": "high"},
        {"title": "Presentación programada", "offset_days": 7, "priority": "medium"},
    ],
}


@dataclass(frozen=True)
class Deadline:
    """Computed milestone or procedural deadline for a synthetic matter."""

    matter_id: str
    title: str
    due_date: date
    days_remaining: int
    priority: str = "medium"
    authority: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize the deadline into JSON-safe primitives."""
        return {
            "matter_id": self.matter_id,
            "title": self.title,
            "due_date": self.due_date.isoformat(),
            "days_remaining": self.days_remaining,
            "priority": self.priority,
            "authority": self.authority,
        }


def compute_deadlines(
    matter: Matter,
    rules: dict[str, list[dict[str, Any]]] | None = None,
    reference_date: date | None = None,
) -> list[Deadline]:
    """Compute sorted procedural deadlines for a given Matter."""
    rule_book = rules if rules is not None else DEFAULT_DEADLINE_RULES
    key = matter.matter_type.strip().lower()
    applicable_rules = rule_book.get(key) or rule_book.get("default", [])

    anchor = matter.filing_date or matter.created_at.date()
    ref = reference_date or date.today()

    deadlines: list[Deadline] = []
    for rule in applicable_rules:
        offset = int(rule.get("offset_days", 0))
        due = anchor + timedelta(days=offset)
        deadlines.append(
            Deadline(
                matter_id=matter.id,
                title=str(rule["title"]),
                due_date=due,
                days_remaining=(due - ref).days,
                priority=str(rule.get("priority", "medium")),
                authority=matter.authority,
            )
        )

    deadlines.sort(key=lambda item: (item.due_date, item.title))
    return deadlines


def list_upcoming(
    matters: Iterable[Matter],
    within_days: int | None = 30,
    reference_date: date | None = None,
    rules: dict[str, list[dict[str, Any]]] | None = None,
) -> list[Deadline]:
    """Return deadlines across matters due within the specified day horizon."""
    ref = reference_date or date.today()
    upcoming: list[Deadline] = []
    for matter in matters:
        for deadline in compute_deadlines(matter, rules=rules, reference_date=ref):
            if deadline.days_remaining < 0:
                continue
            if within_days is not None and deadline.days_remaining > within_days:
                continue
            upcoming.append(deadline)

    upcoming.sort(key=lambda item: (item.due_date, item.matter_id, item.title))
    return upcoming
