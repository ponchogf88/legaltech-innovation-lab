"""Security, PII, secret, and AI governance guardrails for LegalTech Lab.

Enforces the strict synthetic-data-only boundary across intake payloads,
rendered documents, and repository files, and evaluates mandatory Human-in-the-Loop
(EU AI Act + LFPDPPP) governance readiness controls.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

GOVERNANCE_FRAMEWORK = "EU AI Act + LFPDPPP + HITL Lab Policy"

REQUIRED_GOVERNANCE_CONTROLS: tuple[str, ...] = (
    "human_in_the_loop",
    "synthetic_data_only",
    "mock_authority_only",
    "audit_trail_enabled",
    "fact_conclusion_separation",
    "pii_guard_enabled",
)

# SAT official generic RFCs reserved for public/foreign synthetic placeholders.
_ALLOWED_SYNTHETIC_RFCS: frozenset[str] = frozenset({
    "XAXX010101000",
    "XEXX010101000",
})

_RFC_RE = re.compile(
    r"(?<![A-ZÑ&0-9])([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})(?![A-ZÑ&0-9])",
    flags=re.IGNORECASE,
)
_CURP_RE = re.compile(
    r"\b[A-Z][AEIOUX][A-Z]{2}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b",
    flags=re.IGNORECASE,
)
# Negative lookaround around dots avoids false positives on high-precision floats;
# [ -]? allows catching 18-digit CLABEs obfuscated with spaces or hyphens.
_CLABE_RE = re.compile(r"(?<![\d.])\b(?:\d[ -]?){17}\d\b(?!\.)")


def _compile_fragments(
    fragment_groups: tuple[tuple[str, ...], ...],
    flags: int = 0,
) -> tuple[re.Pattern[str], ...]:
    """Assemble regexes from fragments so source files do not trigger self-scans."""
    return tuple(re.compile("".join(parts), flags) for parts in fragment_groups)


_SECRET_TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = _compile_fragments((
    (r"(?<![A-Za-z0-9_])", "gh", "[pousr]_", "[A-Za-z0-9]{20,}"),
    (r"(?<![A-Za-z0-9_])", "sk", "-", "(?:proj-|live-|test-)?", "[A-Za-z0-9]{20,}"),
    (r"(?<![A-Za-z0-9_])", "AI", "za", r"[0-9A-Za-z\-_]{30,}"),
))

_PRIVATE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = _compile_fragments((
    ("BEGIN ", "(?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?", "PRIVATE ", "KEY"),
))

_REAL_CASE_PATTERNS: tuple[re.Pattern[str], ...] = _compile_fragments(
    (
        (r"(?<!\d)", "920", "/", "2025", r"(?!\d)"),
        (r"(?<!\d)", "1058", "/", "2022", r"(?!\d)"),
        (r"(?<!\d)", "1278", "/", "2021", r"(?!\d)"),
        (r"\b", "Nava", r"\s+", "Correa", r"\b"),
        (r"\b", "Mart", "[íi]", "nez", r"\s+", "Moreno", r"\b"),
        (r"\b", "Trevi", "[ñn]", "o", r"\s+", "Garza", r"\b"),
        (r"\b", "Victoria", r"\s+", "Monarca", r"\b"),
        (r"\b", "magaly", "[-_]", "all", r"\b"),
    ),
    flags=re.IGNORECASE,
)

_TAG_PATTERNS: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = (
    ("CURP_PATTERN", (_CURP_RE,)),
    ("CLABE_PATTERN", (_CLABE_RE,)),
    ("SECRET_TOKEN", _SECRET_TOKEN_PATTERNS),
    ("PRIVATE_KEY_HEADER", _PRIVATE_KEY_PATTERNS),
    ("REAL_CASE_MARKER", _REAL_CASE_PATTERNS),
)

_SKIP_DIRS: frozenset[str] = frozenset({
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".vite",
})

_BINARY_EXTENSIONS: frozenset[str] = frozenset({
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".bmp",
    ".tiff",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".mp3",
    ".mp4",
    ".mov",
    ".wav",
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".cer",
    ".der",
    ".p12",
    ".pfx",
})


class SecurityViolationError(ValueError):
    """Raised when PII, credentials, or quarantined real-case data are detected."""


def _has_non_synthetic_rfc(text: str) -> bool:
    """Return True if text contains a Mexican RFC outside the synthetic allowlist."""
    return any(
        match.group(1).upper() not in _ALLOWED_SYNTHETIC_RFCS
        for match in _RFC_RE.finditer(text)
    )


def scan_text_for_pii_or_real_cases(text: str) -> list[str]:
    """Scan text for Mexican PII (RFC, CURP, CLABE), secrets, and real-case markers.

    Returns a deduplicated list of finding tags in deterministic order.
    """
    if not text:
        return []

    findings: list[str] = []
    if _has_non_synthetic_rfc(text):
        findings.append("RFC_PATTERN")

    for tag, patterns in _TAG_PATTERNS:
        if any(pattern.search(text) for pattern in patterns):
            findings.append(tag)

    return findings


def assert_synthetic_and_safe(payload: dict[str, Any] | str) -> None:
    """Validate that a payload contains only safe synthetic content.

    Raises SecurityViolationError listing detected finding tags if unsafe.
    """
    if isinstance(payload, str):
        serialized = payload
    elif isinstance(payload, (dict, list, tuple)):
        # ensure_ascii=False preserves accented characters and Ñ for pattern matching.
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    else:
        serialized = str(payload)

    findings = scan_text_for_pii_or_real_cases(serialized)
    if findings:
        raise SecurityViolationError(
            "Payload blocked by security guardrail; findings: " + ", ".join(findings)
        )


def evaluate_governance_readiness(agent_config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate mandatory EU AI Act, LFPDPPP, and HITL Lab Policy controls."""
    if not isinstance(agent_config, dict):
        raise TypeError("agent_config must be a dict")

    failed_controls = [
        control
        for control in REQUIRED_GOVERNANCE_CONTROLS
        if agent_config.get(control) is not True
    ]
    total = len(REQUIRED_GOVERNANCE_CONTROLS)
    score = total - len(failed_controls)

    return {
        "passed": len(failed_controls) == 0,
        "score": score,
        "total": total,
        "failed_controls": failed_controls,
        "framework": GOVERNANCE_FRAMEWORK,
    }


def _is_skipped_dir(dirname: str) -> bool:
    """Return True if a directory name should be pruned during repository walks."""
    return dirname in _SKIP_DIRS or dirname.endswith(".egg-info")


def _is_skipped_file(path: Path) -> bool:
    """Return True if a file is metadata or has a known binary extension."""
    if path.name in {".git", ".DS_Store"}:
        return True
    return path.suffix.lower() in _BINARY_EXTENSIONS


def scan_repository_tree(root: Path) -> list[dict[str, Any]]:
    """Walk a repository tree and return findings for any UTF-8 text file with violations."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Repository root does not exist: {root_path}")

    violations: list[dict[str, Any]] = []
    for current_root, dirnames, filenames in os.walk(root_path, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not _is_skipped_dir(d))
        current_path = Path(current_root)

        for filename in sorted(filenames):
            candidate = current_path / filename
            if candidate.is_symlink() or _is_skipped_file(candidate):
                continue
            try:
                content = candidate.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            findings = scan_text_for_pii_or_real_cases(content)
            if findings:
                violations.append({
                    "file": candidate.relative_to(root_path).as_posix(),
                    "findings": findings,
                })

    return violations
