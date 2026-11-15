"""Persistent project continuity, 72-hour immutable clock, task queue, and checkpoint recovery."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
from typing import Any

CLOCK_FILENAME = "72H_CLOCK.json"
STATE_FILENAME = "PROJECT_STATE.json"
CHECKPOINT_FILENAME = "CHECKPOINT.json"

CONFIRMED_START_ISO = "2026-11-15T14:03:47-06:00"
CLOCK_DURATION_HOURS = 72
CLOCK_DURATION_SECONDS = CLOCK_DURATION_HOURS * 3600

REQUIRED_TASK_FIELDS: tuple[str, ...] = (
    "task_id",
    "description",
    "priority",
    "dependencies",
    "assigned_agent",
    "status",
    "acceptance_criteria",
    "evidence_of_completion",
)

VALID_TASK_STATUSES: frozenset[str] = frozenset({
    "DONE",
    "IN_PROGRESS",
    "READY",
    "QUEUED",
    "BLOCKED",
    "BACKLOG",
})

_ELIGIBLE_NEXT_STATUSES: frozenset[str] = frozenset({"READY", "QUEUED", "BACKLOG"})
_PRIORITY_RANK: dict[str, int] = {"P0": 0, "P1": 1, "P2": 2}
_STATUS_RANK: dict[str, int] = {"READY": 0, "QUEUED": 1, "BACKLOG": 2}


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_duration_hms(seconds: float | int) -> str:
    """Format a non-negative duration in seconds as ``HHh MMm SSs``."""
    total_seconds = max(0, int(seconds))
    hours, rem = divmod(total_seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"


def _validate_clock_payload(payload: dict[str, Any]) -> None:
    required_keys = (
        "immutable_start_iso",
        "immutable_start_utc",
        "deadline_iso",
        "deadline_utc",
        "duration_hours",
    )
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"72H clock payload missing required keys: {', '.join(missing)}")
    if payload.get("duration_hours") != CLOCK_DURATION_HOURS:
        raise ValueError(
            f"72H clock duration_hours must equal {CLOCK_DURATION_HOURS}, "
            f"got {payload.get('duration_hours')!r}"
        )


def init_72h_clock(
    clock_path: Path,
    start_iso: str = CONFIRMED_START_ISO,
    created_by_commit: str = "8d3ad92",
) -> dict[str, Any]:
    """Initialize an immutable 72-hour project clock.

    Raises FileExistsError if the clock file already exists so the start
    timestamp and 72-hour deadline can never be overwritten or reset automatically.
    """
    clock_path = Path(clock_path)
    if clock_path.exists():
        existing = json.loads(clock_path.read_text(encoding="utf-8"))
        _validate_clock_payload(existing)
        raise FileExistsError(
            "72H_CLOCK.json already exists and is immutable; never reset automatically."
        )

    start_dt = datetime.fromisoformat(start_iso)
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)

    deadline_dt = start_dt + timedelta(hours=CLOCK_DURATION_HOURS)
    start_utc = _to_utc(start_dt)
    deadline_utc = _to_utc(deadline_dt)

    payload: dict[str, Any] = {
        "clock_id": "LEGALTECH-72H-MISSION-CLOCK",
        "protocol": "LEGALTECH-CONTINUOUS-ENGINEERING-PROTOCOL",
        "immutable_start_iso": start_dt.isoformat(),
        "immutable_start_utc": start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "deadline_iso": deadline_dt.isoformat(),
        "deadline_utc": deadline_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_hours": CLOCK_DURATION_HOURS,
        "duration_seconds": CLOCK_DURATION_SECONDS,
        "auto_reset_allowed": False,
        "survives_restarts": True,
        "created_by_commit": created_by_commit,
    }
    clock_path.parent.mkdir(parents=True, exist_ok=True)
    clock_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def load_or_init_72h_clock(
    clock_path: Path,
    start_iso: str = CONFIRMED_START_ISO,
    created_by_commit: str = "8d3ad92",
) -> dict[str, Any]:
    """Load an existing immutable clock untouched or initialize it once if absent."""
    clock_path = Path(clock_path)
    if clock_path.exists():
        payload = json.loads(clock_path.read_text(encoding="utf-8"))
        _validate_clock_payload(payload)
        return payload
    return init_72h_clock(clock_path, start_iso=start_iso, created_by_commit=created_by_commit)


def compute_clock_status(clock_path: Path, now: datetime | None = None) -> dict[str, Any]:
    """Compute live elapsed and remaining countdown from system time without mutating clock file."""
    clock_path = Path(clock_path)
    payload = json.loads(clock_path.read_text(encoding="utf-8"))
    _validate_clock_payload(payload)

    start_utc = _to_utc(datetime.fromisoformat(payload["immutable_start_utc"]))
    deadline_utc = _to_utc(datetime.fromisoformat(payload["deadline_utc"]))
    now_utc = _to_utc(now if now is not None else datetime.now(timezone.utc))

    elapsed_seconds = max(0, int((now_utc - start_utc).total_seconds()))
    remaining_seconds = max(0, int((deadline_utc - now_utc).total_seconds()))
    progress_pct = round(min(100.0, (elapsed_seconds / CLOCK_DURATION_SECONDS) * 100.0), 2)

    return {
        **payload,
        "evaluated_at_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_seconds": elapsed_seconds,
        "remaining_seconds": remaining_seconds,
        "elapsed_human": format_duration_hms(elapsed_seconds),
        "remaining_human": format_duration_hms(remaining_seconds),
        "progress_pct": progress_pct,
        "is_expired": now_utc >= deadline_utc,
    }


def validate_task_queue(tasks: Sequence[dict[str, Any]]) -> list[str]:
    """Validate task queue schema and return human-readable error strings."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            errors.append(f"Task at index {index} is not an object.")
            continue

        missing = [field for field in REQUIRED_TASK_FIELDS if field not in task]
        if missing:
            errors.append(
                f"Task {task.get('task_id', f'#{index}')} missing fields: {', '.join(missing)}"
            )

        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"Task at index {index} has invalid empty task_id.")
        elif task_id in seen_ids:
            errors.append(f"Duplicate task_id detected: {task_id}")
        else:
            seen_ids.add(task_id)

        status = task.get("status")
        if status not in VALID_TASK_STATUSES:
            errors.append(
                f"Task {task_id or f'#{index}'} has invalid status {status!r}; "
                f"expected one of {sorted(VALID_TASK_STATUSES)}"
            )

        deps = task.get("dependencies")
        if deps is not None and not isinstance(deps, list):
            errors.append(f"Task {task_id or f'#{index}'} dependencies must be a list.")

        criteria = task.get("acceptance_criteria")
        if isinstance(criteria, str):
            if not criteria.strip():
                errors.append(f"Task {task_id or f'#{index}'} acceptance_criteria must be non-empty.")
        elif isinstance(criteria, list):
            if len(criteria) == 0 or not all(isinstance(c, str) and c.strip() for c in criteria):
                errors.append(
                    f"Task {task_id or f'#{index}'} acceptance_criteria list must contain non-empty strings."
                )
        elif "acceptance_criteria" in task:
            errors.append(
                f"Task {task_id or f'#{index}'} acceptance_criteria must be a non-empty string or list."
            )

    return errors


def identify_next_unblocked_task(tasks: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the highest-priority pending task whose dependencies are all DONE."""
    status_by_id = {
        task["task_id"]: task.get("status")
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("task_id"), str)
    }

    candidates: list[tuple[int, int, int, dict[str, Any]]] = []
    for idx, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue
        status = task.get("status")
        if status not in _ELIGIBLE_NEXT_STATUSES:
            continue
        deps = task.get("dependencies") or []
        if all(status_by_id.get(dep) == "DONE" for dep in deps):
            prio_rank = _PRIORITY_RANK.get(str(task.get("priority", "")).upper(), 99)
            status_rank = _STATUS_RANK.get(str(status), 99)
            candidates.append((prio_rank, status_rank, idx, task))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    return candidates[0][3]


def _run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def inspect_git_state(repo_root: Path) -> dict[str, Any]:
    """Inspect active Git branch, commit hashes, and porcelain working-tree status."""
    repo_root = Path(repo_root)
    branch = _run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    head_commit = _run_git(repo_root, "rev-parse", "HEAD").strip()
    short_commit = _run_git(repo_root, "rev-parse", "--short", "HEAD").strip()
    porcelain = _run_git(repo_root, "status", "--porcelain")
    uncommitted_changes = [line.rstrip("\n") for line in porcelain.splitlines() if line.strip()]
    return {
        "branch": branch,
        "head_commit": head_commit,
        "short_commit": short_commit,
        "uncommitted_changes": uncommitted_changes,
        "is_clean": len(uncommitted_changes) == 0,
    }


def save_checkpoint(
    repo_root: Path,
    last_completed_operation: str,
    state_path: Path | None = None,
    checkpoint_path: Path | None = None,
    clock_path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Persist a deterministic crash/interruption recovery checkpoint to CHECKPOINT.json."""
    repo_root = Path(repo_root)
    resolved_state = Path(state_path) if state_path is not None else repo_root / STATE_FILENAME
    resolved_checkpoint = (
        Path(checkpoint_path) if checkpoint_path is not None else repo_root / CHECKPOINT_FILENAME
    )
    resolved_clock = Path(clock_path) if clock_path is not None else repo_root / CLOCK_FILENAME

    state_data = json.loads(resolved_state.read_text(encoding="utf-8"))
    tasks = state_data.get("tasks", [])
    task_errors = validate_task_queue(tasks)
    if task_errors:
        raise ValueError(f"Cannot save checkpoint with invalid task queue: {task_errors}")

    now_utc = _to_utc(now if now is not None else datetime.now(timezone.utc))
    clock_status = compute_clock_status(resolved_clock, now=now_utc)
    git_state = inspect_git_state(repo_root)

    remaining_tasks = [
        {
            "task_id": t["task_id"],
            "priority": t["priority"],
            "status": t["status"],
            "assigned_agent": t["assigned_agent"],
            "description": t["description"],
        }
        for t in tasks
        if t.get("status") != "DONE"
    ]
    next_task = identify_next_unblocked_task(tasks)
    next_task_summary = (
        f"{next_task['task_id']} ({next_task['description']})"
        if next_task is not None
        else "None (review BLOCKED gates or completion status)"
    )

    checkpoint_payload: dict[str, Any] = {
        "checkpoint_id": f"CHK-{now_utc.strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_completed_operation": last_completed_operation,
        "current_branch": git_state["branch"],
        "current_git_commit": git_state["head_commit"],
        "current_git_short_commit": git_state["short_commit"],
        "uncommitted_changes": git_state["uncommitted_changes"],
        "clock_status": {
            "immutable_start_iso": clock_status["immutable_start_iso"],
            "deadline_iso": clock_status["deadline_iso"],
            "elapsed_human": clock_status["elapsed_human"],
            "remaining_human": clock_status["remaining_human"],
            "progress_pct": clock_status["progress_pct"],
            "is_expired": clock_status["is_expired"],
        },
        "remaining_tasks": remaining_tasks,
        "next_executable_task": next_task,
        "recovery_instructions": [
            f"1. Verify repository is on branch '{git_state['branch']}' (do not reset completed DONE tasks or 72H_CLOCK.json).",
            "2. Run `git status -sb` and preserve or inspect any listed uncommitted_changes before taking action.",
            "3. Run `.venv/bin/python -m legal_engine.cli clock` and `.venv/bin/python -m legal_engine.cli state` to reload live countdown and queue validation.",
            "4. Run `.venv/bin/pytest -v` and `.venv/bin/python -m legal_engine.cli security-check` to establish verified baseline health.",
            f"5. Resume execution directly from next_executable_task: {next_task_summary}.",
        ],
    }

    resolved_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    resolved_checkpoint.write_text(
        json.dumps(checkpoint_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return checkpoint_payload
