"""Red Team QA Challenge from DELL_WINDOWS_LAB:
Exposes real PII guardrail bypasses in packages/legal_engine/security.py
(lowercase RFC/CURP evasion and spaced/hyphenated CLABE evasion).
"""

from __future__ import annotations

import pytest
from legal_engine.security import (
    SecurityViolationError,
    assert_synthetic_and_safe,
    scan_text_for_pii_or_real_cases,
)


def test_redteam_lowercase_rfc_must_be_blocked() -> None:
    """Nomos guardrail must detect non-synthetic RFCs even when entered in lowercase."""
    lowercase_rfc = "gode" + "561231" + "gr8"
    evasive_payload = f"Cliente con rfc real en minusculas: {lowercase_rfc} dentro del escrito."
    findings = scan_text_for_pii_or_real_cases(evasive_payload)
    assert "RFC_PATTERN" in findings, (
        f"RED TEAM FAIL: security.py allowed a lowercase RFC ({lowercase_rfc}) to bypass _RFC_RE!"
    )
    with pytest.raises(SecurityViolationError):
        assert_synthetic_and_safe({"facts": evasive_payload})


def test_redteam_spaced_clabe_must_be_blocked() -> None:
    """Nomos guardrail must detect 18-digit CLABE numbers even when formatted with spaces or hyphens."""
    spaced_clabe = "012 " + "180 " + "001234" + "56789 " + "0"
    evasive_clabe = f"Depositar pension alimenticia en CLABE {spaced_clabe} del banco."
    findings = scan_text_for_pii_or_real_cases(evasive_clabe)
    assert "CLABE_PATTERN" in findings, (
        "RED TEAM FAIL: security.py allowed a space-separated 18-digit CLABE to bypass _CLABE_RE!"
    )
