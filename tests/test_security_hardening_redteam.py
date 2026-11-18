"""Hardening tests addressing all 4 Dell Argon Red Team audit findings."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import threading
import urllib.error
import urllib.request

import pytest

from legal_engine.api import MAX_REQUEST_BODY_BYTES, create_server
from legal_engine.audit import AuditLog
from legal_engine.security import scan_text_for_pii_or_real_cases


def _multiprocess_worker(args: tuple[str, int, int]) -> None:
    log_path, worker_id, count = args
    audit = AuditLog(log_path)
    for idx in range(count):
        audit.record(
            actor=f"worker-{worker_id}",
            action="concurrent_ping",
            matter_id="EXP-SINT-2026-001",
            details={"worker": worker_id, "seq": idx},
        )


def test_redteam_finding_1_curp_lowercase_and_hyphen_clabe_and_synthetic_rfc_allowed() -> None:
    lower_curp = "aaaa" + "900101" + "h" + "df" + "rrr" + "0" + "9"
    assert scan_text_for_pii_or_real_cases(f"curp {lower_curp}") == ["CURP_PATTERN"]

    hyphen_clabe = "012-" + "180-" + "001234" + "-56789-" + "0"
    assert scan_text_for_pii_or_real_cases(f"clabe {hyphen_clabe}") == ["CLABE_PATTERN"]

    assert scan_text_for_pii_or_real_cases("rfc xaxx010101000") == []


def test_redteam_findings_2_and_3_api_dos_cors_and_token_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, repo = create_server(
        host="127.0.0.1",
        port=0,
        db_path=tmp_path / "hardened.db",
        audit_path=tmp_path / "hardened.audit.jsonl",
    )
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        # 1. Malformed Content-Length -> HTTP 400 invalid_content_length
        req_bad_len = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/matters",
            data=b"{}",
            method="POST",
            headers={"Content-Type": "application/json", "Content-Length": "not-an-int"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc_bad:
            urllib.request.urlopen(req_bad_len, timeout=5)
        assert exc_bad.value.code == 400

        # 2. Oversized Content-Length -> HTTP 413 payload_too_large without reading gigabytes
        req_huge = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/matters",
            data=b"{}",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(MAX_REQUEST_BODY_BYTES + 1),
            },
        )
        with pytest.raises(urllib.error.HTTPError) as exc_huge:
            urllib.request.urlopen(req_huge, timeout=5)
        assert exc_huge.value.code == 413

        # 3. Untrusted CORS Origin blocked (HTTP 403), never wildcard *
        req_evil = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/health",
            method="GET",
            headers={"Origin": "https://evil.example"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc_evil:
            urllib.request.urlopen(req_evil, timeout=5)
        assert exc_evil.value.code == 403

        # 4. Trusted GitHub Pages Origin echoed safely (no wildcard '*')
        req_gh = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/health",
            method="GET",
            headers={"Origin": "https://ponchogf88.github.io"},
        )
        with urllib.request.urlopen(req_gh, timeout=5) as resp_gh:
            assert resp_gh.status == 200
            assert resp_gh.headers.get("Access-Control-Allow-Origin") == "https://ponchogf88.github.io"

        # 5. Optional API token enforcement on HITL mutation routes
        monkeypatch.setenv("LEGAL_LAB_API_TOKEN", "sintetico-secret-token-check")
        req_unauth = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/submissions/SUB-NONE/approve",
            data=json.dumps({"reviewer": "Lic. Demo"}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(urllib.error.HTTPError) as exc_unauth:
            urllib.request.urlopen(req_unauth, timeout=5)
        assert exc_unauth.value.code == 401
    finally:
        server.shutdown()
        server.server_close()
        repo.close()
        thread.join(timeout=2)


def test_redteam_finding_4_audit_log_multiprocess_chain_integrity(tmp_path: Path) -> None:
    log_path = tmp_path / "mp-audit.jsonl"
    tasks = [(str(log_path), wid, 10) for wid in range(3)]
    with ProcessPoolExecutor(max_workers=3) as pool:
        list(pool.map(_multiprocess_worker, tasks))

    audit = AuditLog(log_path)
    entries = audit.read_entries()
    assert len(entries) == 30
    assert audit.verify_integrity() is True
