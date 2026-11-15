"""Tests for PII, credential, real-case quarantine, and AI governance guardrails."""

from __future__ import annotations

from pathlib import Path

import pytest

from legal_engine.security import (
    GOVERNANCE_FRAMEWORK,
    REQUIRED_GOVERNANCE_CONTROLS,
    SecurityViolationError,
    assert_synthetic_and_safe,
    evaluate_governance_readiness,
    scan_repository_tree,
    scan_text_for_pii_or_real_cases,
)


def _compliant_config() -> dict[str, bool]:
    return {control: True for control in REQUIRED_GOVERNANCE_CONTROLS}


@pytest.mark.parametrize(
    ("label", "payload", "expected_tag"),
    [
        ("rfc_fisica", "RFC: " + "GODE" + "561231" + "GR8", "RFC_PATTERN"),
        ("rfc_moral", "RFC: " + "EMP" + "210101" + "AB1", "RFC_PATTERN"),
        ("rfc_ampersand", "RFC: " + "&AB" + "210101" + "XY9", "RFC_PATTERN"),
        ("curp", "CURP: " + "AAAA" + "900101" + "H" + "DF" + "RRR" + "0" + "9", "CURP_PATTERN"),
        ("clabe", "CLABE: " + "012180" + "001234" + "567890", "CLABE_PATTERN"),
        ("github_token", "token=" + "ghp_" + "A" * 25, "SECRET_TOKEN"),
        ("sk_token", "key=" + "sk-" + "B" * 24, "SECRET_TOKEN"),
        ("google_api_key", "key=" + "AI" + "za" + "C" * 32, "SECRET_TOKEN"),
        ("private_key", "-----" + "BEGIN " + "PRIVATE " + "KEY-----", "PRIVATE_KEY_HEADER"),
        ("rsa_private_key", "-----" + "BEGIN RSA " + "PRIVATE " + "KEY-----", "PRIVATE_KEY_HEADER"),
        ("openssh_private_key", "-----" + "BEGIN OPENSSH " + "PRIVATE " + "KEY-----", "PRIVATE_KEY_HEADER"),
        ("case_920", "Expediente " + "920" + "/2025", "REAL_CASE_MARKER"),
        ("case_1058", "Expediente " + "1058" + "/2022", "REAL_CASE_MARKER"),
        ("case_1278", "Expediente " + "1278" + "/2021", "REAL_CASE_MARKER"),
        ("marker_nava", "Cliente: " + "Nava " + "Correa", "REAL_CASE_MARKER"),
        ("marker_martinez_accent", "Parte: " + "Martínez " + "Moreno", "REAL_CASE_MARKER"),
        ("marker_martinez_plain", "Parte: " + "martinez " + "moreno", "REAL_CASE_MARKER"),
        ("marker_trevino_accent", "Parte: " + "Treviño " + "Garza", "REAL_CASE_MARKER"),
        ("marker_trevino_plain", "Parte: " + "Trevino " + "Garza", "REAL_CASE_MARKER"),
        ("marker_victoria", "Calle " + "Victoria " + "Monarca", "REAL_CASE_MARKER"),
        ("marker_magaly", "legacy/" + "magaly" + "-all", "REAL_CASE_MARKER"),
    ],
)
def test_scan_detects_forbidden_patterns(
    label: str,
    payload: str,
    expected_tag: str,
) -> None:
    findings = scan_text_for_pii_or_real_cases(payload)
    assert expected_tag in findings, f"{label} did not trigger {expected_tag}: {findings}"


def test_curp_does_not_false_positive_as_rfc() -> None:
    synthetic_curp = "AAAA" + "900101" + "H" + "DF" + "RRR" + "0" + "9"
    assert scan_text_for_pii_or_real_cases(synthetic_curp) == ["CURP_PATTERN"]


@pytest.mark.parametrize(
    "clean_payload",
    [
        "",
        "María Ejemplo García (cliente sintético)",
        "EXP-SINT-2026-001",
        "XAXX010101000",
        "XEXX010101000",
        "Timestamp 1700000000 and float " + "0." + "123456" * 3,
        "Digest " + "ab12" * 16,
        {
            "matter_id": "EXP-SINT-2026-001",
            "client_name": "María Ejemplo García (cliente sintético)",
            "rfc": "XAXX010101000",
            "facts": "Solicitud simulada sin datos reales.",
        },
    ],
)
def test_clean_synthetic_payloads_pass(clean_payload: dict | str) -> None:
    if isinstance(clean_payload, str):
        assert scan_text_for_pii_or_real_cases(clean_payload) == []
    assert_synthetic_and_safe(clean_payload)


@pytest.mark.parametrize(
    ("unsafe_payload", "expected_tag"),
    [
        ("CLABE " + "012180" + "001234" + "567890", "CLABE_PATTERN"),
        (
            {
                "client_name": "Persona " + "Treviño " + "Garza",
                "matter_id": "EXP-SINT-2026-002",
            },
            "REAL_CASE_MARKER",
        ),
        (
            {
                "rfc": "GODE" + "561231" + "GR8",
                "api_token": "ghp_" + "X" * 24,
            },
            "RFC_PATTERN",
        ),
    ],
)
def test_assert_synthetic_and_safe_raises_security_violation(
    unsafe_payload: dict | str,
    expected_tag: str,
) -> None:
    with pytest.raises(SecurityViolationError, match=expected_tag):
        assert_synthetic_and_safe(unsafe_payload)


def test_evaluate_governance_readiness_compliant() -> None:
    result = evaluate_governance_readiness(_compliant_config())
    assert result == {
        "passed": True,
        "score": 6,
        "total": 6,
        "failed_controls": [],
        "framework": GOVERNANCE_FRAMEWORK,
    }
    assert result["framework"] == "EU AI Act + LFPDPPP + HITL Lab Policy"


def test_evaluate_governance_readiness_non_compliant() -> None:
    config = _compliant_config()
    config["human_in_the_loop"] = False
    result = evaluate_governance_readiness(config)

    assert result["passed"] is False
    assert result["score"] == 5
    assert result["total"] == 6
    assert "human_in_the_loop" in result["failed_controls"]


def test_evaluate_governance_readiness_requires_strict_boolean_true() -> None:
    config = _compliant_config()
    config["pii_guard_enabled"] = 1  # type: ignore[assignment]
    result = evaluate_governance_readiness(config)

    assert result["passed"] is False
    assert "pii_guard_enabled" in result["failed_controls"]

    empty_result = evaluate_governance_readiness({})
    assert empty_result["passed"] is False
    assert empty_result["score"] == 0
    assert empty_result["failed_controls"] == list(REQUIRED_GOVERNANCE_CONTROLS)


def test_scan_repository_tree_filters_ignored_and_flags_violations(tmp_path: Path) -> None:
    (tmp_path / "clean.txt").write_text("EXP-SINT-2026-001", encoding="utf-8")
    (tmp_path / "bad.json").write_text(
        '{"case": "' + "920" + "/2025" + '"}',
        encoding="utf-8",
    )
    (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"ghp_" + b"A" * 25)
    (tmp_path / "invalid_utf8.txt").write_bytes(b"\xff\xfe\x00" + b"sk-" + b"B" * 25)

    for skipped_dir in (".git", ".venv", "node_modules", "dist", "__pycache__", ".pytest_cache"):
        d = tmp_path / skipped_dir
        d.mkdir()
        (d / "secret.txt").write_text("ghp_" + "Z" * 25, encoding="utf-8")

    violations = scan_repository_tree(tmp_path)
    assert violations == [
        {"file": "bad.json", "findings": ["REAL_CASE_MARKER"]},
    ]


def test_scan_repository_tree_is_clean_on_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    assert scan_repository_tree(repo_root) == []
