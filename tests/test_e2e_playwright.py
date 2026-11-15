"""Pytest wrapper executing headless Playwright E2E checks against Command Center UI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import pytest


def test_command_center_e2e_playwright() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "tests" / "e2e" / "command_center_e2e.mjs"
    assert script_path.is_file(), f"Missing Playwright script: {script_path}"

    env = os.environ.copy()
    if Path("/Users/user/node_modules").is_dir() and not env.get("NODE_PATH"):
        env["NODE_PATH"] = "/Users/user/node_modules"

    proc = subprocess.run(
        ["node", str(script_path)],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if proc.returncode != 0:
        pytest.fail(
            f"Playwright E2E script failed (exit={proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    payload = json.loads(proc.stdout)
    assert payload["status"] == "PASSED"
    assert payload["checks_passed"] == 6
    assert payload["case_id"] == "EXP-SINT-2026-001"
    assert payload["evidence_validated_counter"] == "1/3 validadas"
    assert payload["receipt_folio"] == "MOCK-TV-EXP-SINT-2026-001-001"
    assert payload["audit_entries_count"] == 10
    assert payload["audit_chain_valid"] is True
    assert payload["browser_errors"] == []
