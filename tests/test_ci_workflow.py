"""Contract verification tests for the GitHub Actions CI Quality & Security Gate."""

from __future__ import annotations

from pathlib import Path
import re


def test_ci_quality_security_workflow_contract() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow_path = repo_root / ".github" / "workflows" / "ci-quality-security.yml"
    assert workflow_path.is_file(), f"Missing CI workflow: {workflow_path}"

    raw = workflow_path.read_text(encoding="utf-8")

    # Enforce least-privilege token scope
    assert re.search(r"permissions:\s*\n\s*contents:\s*read", raw), "Missing least-privilege contents: read permission"

    # Enforce branch triggers for main and dev/**
    for branch_token in ("main", '"dev/**"'):
        assert branch_token in raw, f"Missing branch trigger {branch_token}"

    # Verify both jobs exist
    assert "backend-security-and-tests:" in raw
    assert "frontend-build-and-e2e:" in raw

    # Verify mandatory security, test, continuity, build, and E2E gates
    required_commands = (
        "python -m legal_engine.cli security-check",
        "pytest -v",
        "python -m legal_engine.cli demo --stop-before-submit",
        "python -m legal_engine.cli verify-audit",
        "python -m legal_engine.cli clock",
        "python -m legal_engine.cli state",
        "npm run build",
        "npm run test:e2e",
    )
    for cmd in required_commands:
        assert cmd in raw, f"CI workflow missing mandatory gate command: {cmd}"

    # Verify no tabs (invalid YAML indentation)
    assert "\t" not in raw, "YAML workflow must not contain tab characters"
