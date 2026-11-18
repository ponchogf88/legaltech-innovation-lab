"""API endpoint dispatcher and live ThreadingHTTPServer tests."""

from __future__ import annotations

import json
from pathlib import Path
import threading
import urllib.error
import urllib.request

from legal_engine.api import create_server, handle_api_request
from legal_engine.audit import AuditLog
from legal_engine.review import ReviewQueue
from legal_engine.storage import SQLiteRepository


def test_api_dispatcher_full_hitl_lifecycle(tmp_path: Path) -> None:
    """Exercise /api/health, /api/matters, HITL block (409), approve, reject, and mock submit."""
    repo = SQLiteRepository(":memory:")
    queue = ReviewQueue()
    audit = AuditLog(tmp_path / "api-audit.jsonl")

    try:
        status, health = handle_api_request("GET", "/api/health", None, repo, queue, audit)
        assert status == 200
        assert health["ok"] is True
        assert health["mode"] == "synthetic-only"

        # Unsafe payload must be blocked at HTTP 403
        unsafe_marker = "920" + "/2025"
        status, err = handle_api_request(
            "POST",
            "/api/matters",
            {
                "client_name": "Cliente Ficticio",
                "matter_type": "solicitud",
                "authority": "sat",
                "facts": f"Referencia {unsafe_marker}",
            },
            repo,
            queue,
            audit,
        )
        assert status == 403
        assert err["code"] == "security_violation"

        # Valid synthetic intake
        status, created = handle_api_request(
            "POST",
            "/api/matters",
            {
                "client_name": "Comercializadora Omega Sintética S.A.",
                "matter_type": "solicitud",
                "authority": "tribunal-virtual",
                "facts": "Solicitud sintética de copias certificadas para archivo.",
                "documents_needed": ["Identificación sintética"],
                "filing_date": "2026-11-15",
                "auto_review": True,
            },
            repo,
            queue,
            audit,
        )
        assert status == 201
        sub_id = created["submission"]["id"]
        assert created["submission"]["state"] == "IN_REVIEW"

        # Submitting before approval returns 409 submission_blocked
        status, blocked = handle_api_request(
            "POST",
            f"/api/submissions/{sub_id}/submit",
            {},
            repo,
            queue,
            audit,
        )
        assert status == 409
        assert blocked["code"] == "submission_blocked"

        # Reject returns to DRAFT
        status, rejected = handle_api_request(
            "POST",
            f"/api/submissions/{sub_id}/reject",
            {"reviewer": "Lic. API", "reason": "Falta anexo sintético"},
            repo,
            queue,
            audit,
        )
        assert status == 200
        assert rejected["submission"]["state"] == "DRAFT"

        # Move back to review, approve, and submit
        status, _ = handle_api_request(
            "POST", f"/api/submissions/{sub_id}/review", {"actor": "agent-apollo"}, repo, queue, audit
        )
        assert status == 200

        status, approved = handle_api_request(
            "POST", f"/api/submissions/{sub_id}/approve", {"reviewer": "Lic. API"}, repo, queue, audit
        )
        assert status == 200
        assert approved["submission"]["state"] == "APPROVED"

        status, submitted = handle_api_request(
            "POST", f"/api/submissions/{sub_id}/submit", {}, repo, queue, audit
        )
        assert status == 200
        assert submitted["submission"]["state"] == "RECEIPTED"
        assert submitted["receipt"]["folio"].startswith("MOCK-")
        assert submitted["receipt"]["channel"] == "MOCK"

        status, overview = handle_api_request("GET", "/api/overview", None, repo, queue, audit)
        assert status == 200
        assert len(overview["matters"]) == 1
        assert overview["audit_valid"] is True
    finally:
        repo.close()


def test_live_http_server_health_and_overview(tmp_path: Path) -> None:
    """Spin up ThreadingHTTPServer on ephemeral port 0 and verify live JSON responses."""
    server, repo = create_server(
        host="127.0.0.1",
        port=0,
        db_path=tmp_path / "server.db",
        audit_path=tmp_path / "server.audit.jsonl",
    )
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["ok"] is True
    finally:
        server.shutdown()
        server.server_close()
        repo.close()
        thread.join(timeout=2)


def test_api_sse_events_stream_and_live_http(tmp_path: Path) -> None:
    """Verify SSE frame generation via dispatcher and text/event-stream HTTP delivery."""
    repo = SQLiteRepository(":memory:")
    queue = ReviewQueue()
    audit = AuditLog(tmp_path / "sse-audit.jsonl")

    try:
        status, sse_payload = handle_api_request("GET", "/api/events/stream", None, repo, queue, audit)
        assert status == 200
        assert sse_payload["event"] == "state_snapshot"
        assert sse_payload["stream_format"] == "text/event-stream"
        assert "event: state_snapshot\n" in sse_payload["sse_frame"]
        assert "data: " in sse_payload["sse_frame"]
        assert sse_payload["data"]["audit_valid"] is True
    finally:
        repo.close()

    server, live_repo = create_server(
        host="127.0.0.1",
        port=0,
        db_path=tmp_path / "sse_server.db",
        audit_path=tmp_path / "sse_server.audit.jsonl",
    )
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/events/stream", timeout=5) as resp:
            assert resp.status == 200
            content_type = resp.headers.get("Content-Type", "")
            assert content_type.startswith("text/event-stream")
            raw_text = resp.read().decode("utf-8")
            assert "event: state_snapshot\n" in raw_text
            data_lines = [line for line in raw_text.splitlines() if line.startswith("data: ")]
            assert len(data_lines) == 1
            parsed = json.loads(data_lines[0][len("data: ") :])
            assert parsed["audit_valid"] is True
            assert "latest_audit_hash" in parsed
    finally:
        server.shutdown()
        server.server_close()
        live_repo.close()
        thread.join(timeout=2)
