"""Tests for the immutable 72-hour project clock, task queue continuity, and checkpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess

import pytest

from legal_engine.cli import main as cli_main
from legal_engine.continuity import (
    CLOCK_DURATION_SECONDS,
    CONFIRMED_START_ISO,
    REQUIRED_TASK_FIELDS,
    compute_clock_status,
    identify_next_unblocked_task,
    init_72h_clock,
    load_or_init_72h_clock,
    save_checkpoint,
    validate_task_queue,
)


def _sample_task(
    task_id: str,
    *,
    priority: str = "P0",
    dependencies: list[str] | None = None,
    assigned_agent: str = "Hydrogen",
    status: str = "READY",
) -> dict:
    return {
        "task_id": task_id,
        "description": f"Synthetic task {task_id}",
        "priority": priority,
        "dependencies": dependencies if dependencies is not None else [],
        "assigned_agent": assigned_agent,
        "status": status,
        "acceptance_criteria": [f"Verify {task_id} passes"],
        "evidence_of_completion": "Verified in pytest" if status == "DONE" else "Pending",
    }


def _init_git_repo(repo_dir: Path) -> str:
    subprocess.run(["git", "init", "-b", "dev/mission-002"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Agent"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test-agent@example.invalid"], cwd=repo_dir, check=True)
    readme = repo_dir / "README.md"
    readme.write_text("# Synthetic Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, check=True, capture_output=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_init_72h_clock_creates_exact_deadline_and_enforces_immutability(tmp_path: Path) -> None:
    clock_path = tmp_path / "72H_CLOCK.json"
    created = init_72h_clock(clock_path, start_iso=CONFIRMED_START_ISO, created_by_commit="8d3ad92")

    assert created["immutable_start_iso"] == "2026-11-15T14:03:47-06:00"
    assert created["immutable_start_utc"] == "2026-11-15T20:03:47Z"
    assert created["deadline_iso"] == "2026-11-18T14:03:47-06:00"
    assert created["deadline_utc"] == "2026-11-18T20:03:47Z"
    assert created["duration_hours"] == 72
    assert created["duration_seconds"] == CLOCK_DURATION_SECONDS
    assert created["auto_reset_allowed"] is False

    # Calling init_72h_clock a second time MUST raise FileExistsError and preserve disk bytes.
    raw_before = clock_path.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError, match="immutable"):
        init_72h_clock(clock_path, start_iso="2026-11-16T00:00:00-06:00")
    assert clock_path.read_text(encoding="utf-8") == raw_before

    # load_or_init_72h_clock returns original data untouched even if passed another start_iso.
    loaded = load_or_init_72h_clock(clock_path, start_iso="2026-11-16T00:00:00-06:00")
    assert loaded["immutable_start_iso"] == "2026-11-15T14:03:47-06:00"
    assert loaded["deadline_iso"] == "2026-11-18T14:03:47-06:00"


@pytest.mark.parametrize(
    ("delta", "expected_elapsed", "expected_remaining", "expected_elapsed_str", "expected_remaining_str", "expected_expired"),
    [
        (timedelta(hours=2), 7200, 252000, "02h 00m 00s", "70h 00m 00s", False),
        (timedelta(hours=71, minutes=59, seconds=59), 259199, 1, "71h 59m 59s", "00h 00m 01s", False),
        (timedelta(hours=72), 259200, 0, "72h 00m 00s", "00h 00m 00s", True),
        (timedelta(hours=80), 288000, 0, "80h 00m 00s", "00h 00m 00s", True),
    ],
)
def test_compute_clock_status_at_synthetic_timestamps_without_mutating_file(
    tmp_path: Path,
    delta: timedelta,
    expected_elapsed: int,
    expected_remaining: int,
    expected_elapsed_str: str,
    expected_remaining_str: str,
    expected_expired: bool,
) -> None:
    clock_path = tmp_path / "72H_CLOCK.json"
    init_72h_clock(clock_path, start_iso=CONFIRMED_START_ISO)
    raw_before = clock_path.read_text(encoding="utf-8")

    start_utc = datetime.fromisoformat("2026-11-15T20:03:47+00:00")
    status = compute_clock_status(clock_path, now=start_utc + delta)

    assert status["elapsed_seconds"] == expected_elapsed
    assert status["remaining_seconds"] == expected_remaining
    assert status["elapsed_human"] == expected_elapsed_str
    assert status["remaining_human"] == expected_remaining_str
    assert status["is_expired"] is expected_expired
    assert status["immutable_start_iso"] == "2026-11-15T14:03:47-06:00"
    assert clock_path.read_text(encoding="utf-8") == raw_before


def test_validate_task_queue_enforces_required_fields() -> None:
    valid_tasks = [
        _sample_task("M2-00", status="DONE"),
        _sample_task("M2-01", dependencies=["M2-00"], status="READY"),
    ]
    assert validate_task_queue(valid_tasks) == []

    incomplete = dict(_sample_task("M2-BAD"))
    incomplete.pop("acceptance_criteria")
    errors = validate_task_queue([incomplete])
    assert any("acceptance_criteria" in err for err in errors)
    assert len(REQUIRED_TASK_FIELDS) == 8

    duplicate_tasks = [_sample_task("DUP-1"), _sample_task("DUP-1")]
    dup_errors = validate_task_queue(duplicate_tasks)
    assert any("Duplicate task_id" in err for err in dup_errors)


def test_identify_next_unblocked_task_respects_priority_and_dependencies() -> None:
    tasks = [
        _sample_task("M2-00", priority="P0", dependencies=[], status="DONE"),
        _sample_task("M2-02", priority="P1", dependencies=["M2-01"], status="BACKLOG"),
        _sample_task("M2-03", priority="P1", dependencies=["M2-00"], status="BACKLOG"),
        _sample_task("M2-04", priority="P0", dependencies=["M2-00"], status="QUEUED"),
    ]
    next_task = identify_next_unblocked_task(tasks)
    assert next_task is not None
    assert next_task["task_id"] == "M2-04"


def test_save_checkpoint_and_cli_commands(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    head_sha = _init_git_repo(tmp_path)
    clock_path = tmp_path / "72H_CLOCK.json"
    state_path = tmp_path / "PROJECT_STATE.json"
    checkpoint_path = tmp_path / "CHECKPOINT.json"

    init_72h_clock(clock_path, start_iso=CONFIRMED_START_ISO, created_by_commit=head_sha[:7])
    state_payload = {
        "project": "legaltech-innovation-lab",
        "active_mission": "MISSION 002",
        "completed_missions": ["MISSION 001"],
        "active_blockers": [],
        "tasks": [
            _sample_task("M2-00", status="DONE"),
            _sample_task("M2-01", priority="P0", dependencies=["M2-00"], status="READY"),
        ],
    }
    state_path.write_text(json.dumps(state_payload, indent=2) + "\n", encoding="utf-8")

    # Stage an untracked change to verify uncommitted_changes tracking
    scratch_note = tmp_path / "UNCOMMITTED_NOTE.txt"
    scratch_note.write_text("pending work\n", encoding="utf-8")

    fixed_now = datetime(2026, 11, 15, 22, 3, 47, tzinfo=timezone.utc)
    checkpoint = save_checkpoint(
        repo_root=tmp_path,
        last_completed_operation="Completed M2-00 continuity baseline",
        now=fixed_now,
    )

    assert checkpoint_path.is_file()
    assert checkpoint["last_completed_operation"] == "Completed M2-00 continuity baseline"
    assert checkpoint["current_git_commit"] == head_sha
    assert any("UNCOMMITTED_NOTE.txt" in item for item in checkpoint["uncommitted_changes"])
    assert [t["task_id"] for t in checkpoint["remaining_tasks"]] == ["M2-01"]
    assert len(checkpoint["recovery_instructions"]) >= 5

    # Verify CLI subcommands clock, state, checkpoint return exit 0 and valid JSON.
    assert cli_main(["clock", "--root", str(tmp_path)]) == 0
    clock_out = json.loads(capsys.readouterr().out)
    assert clock_out["immutable_start_iso"] == CONFIRMED_START_ISO

    assert cli_main(["state", "--root", str(tmp_path)]) == 0
    state_out = json.loads(capsys.readouterr().out)
    assert state_out["valid"] is True
    assert state_out["next_executable_task"]["task_id"] == "M2-01"

    assert cli_main(["checkpoint", "--root", str(tmp_path), "--op", "CLI checkpoint test"]) == 0
    chk_out = json.loads(capsys.readouterr().out)
    assert chk_out["last_completed_operation"] == "CLI checkpoint test"
    assert chk_out["current_git_commit"] == head_sha
