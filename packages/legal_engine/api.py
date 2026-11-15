"""Pure-stdlib JSON HTTP API server and testable request dispatcher."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from .audit import AuditLog
from .authorities import UnknownAuthorityError, get_authority
from .deadlines import list_upcoming
from .documents import DocumentRenderError, render_document
from .intake import IntakeValidationError, intake_matter
from .models import Submission, SubmissionState
from .review import ReviewError, ReviewQueue
from .storage import SQLiteRepository
from .submissions import SubmissionBlockedError, submit

try:
    from .security import SecurityViolationError
except ImportError:  # pragma: no cover - optional prior to Workstream C merge
    class _MissingSecurityError(Exception):
        pass

    SecurityViolationError = _MissingSecurityError  # type: ignore[assignment, misc]

_SUBMISSION_ACTION_RE = re.compile(r"^/api/submissions/([^/]+)/(review|approve|reject|submit)$")


def handle_api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None,
    repo: SQLiteRepository,
    queue: ReviewQueue,
    audit: AuditLog | None = None,
) -> tuple[int, dict[str, Any]]:
    """Dispatch an API request cleanly without requiring a live socket."""
    clean_method = method.upper().strip()
    clean_path = urlparse(path).path.rstrip("/") or "/"

    if clean_method == "GET" and clean_path == "/api/health":
        return (200, {"ok": True, "service": "legal-engine", "mode": "synthetic-only"})

    if clean_method == "GET" and clean_path == "/api/overview":
        matters = [item.to_dict() for item in repo.list_matters()]
        documents = [item.to_dict() for item in repo.list_documents()]
        submissions = [item.to_dict() for item in repo.list_submissions()]
        evidence = [item.to_dict() for item in repo.list_evidence()]
        audit_valid = audit.verify_integrity() if audit is not None else True
        return (
            200,
            {
                "matters": matters,
                "documents": documents,
                "submissions": submissions,
                "evidence": evidence,
                "audit_valid": audit_valid,
            },
        )

    if clean_method == "GET" and clean_path == "/api/deadlines":
        deadlines = [item.to_dict() for item in list_upcoming(repo.list_matters(), within_days=None)]
        return (200, {"deadlines": deadlines})

    if clean_method == "GET" and clean_path == "/api/audit":
        entries = audit.read_entries() if audit is not None else []
        audit_valid = audit.verify_integrity() if audit is not None else True
        return (200, {"entries": entries, "audit_valid": audit_valid})

    if clean_method == "POST" and clean_path == "/api/matters":
        if payload is not None and not isinstance(payload, dict):
            return (400, {"error": "Payload must be a JSON object.", "code": "validation_error"})
        data = payload if payload is not None else {}

        raw_template = data.get("template_key", "solicitud_general")
        if not isinstance(raw_template, str) or not raw_template.strip():
            return (
                400,
                {"error": "Field 'template_key' must be a non-empty string.", "code": "validation_error"},
            )
        template_key = raw_template.strip()
        auto_review = bool(data.get("auto_review", False))

        try:
            matter = intake_matter(data)
            document = render_document(matter, template_key=template_key)
        except SecurityViolationError as exc:
            return (403, {"error": str(exc), "code": "security_violation"})
        except (IntakeValidationError, DocumentRenderError, ValueError) as exc:
            return (400, {"error": str(exc), "code": "validation_error"})

        submission = Submission(
            id=f"SUB-{uuid4().hex[:8].upper()}",
            matter_id=matter.id,
            document_id=document.id,
            state=SubmissionState.DRAFT,
        )
        if auto_review:
            queue.submit_for_review(submission, actor="api")
        else:
            queue.register(submission)

        repo.save_matter(matter)
        repo.save_document(document)
        repo.save_submission(submission)

        if audit is not None:
            audit.record(
                actor="api",
                action="matter_intaked",
                matter_id=matter.id,
                details={
                    "document_id": document.id,
                    "submission_id": submission.id,
                    "state": submission.state.value,
                    "authority": matter.authority,
                    "auto_review": auto_review,
                },
            )

        return (
            201,
            {
                "matter": matter.to_dict(),
                "document": document.to_dict(),
                "submission": submission.to_dict(),
            },
        )

    match = _SUBMISSION_ACTION_RE.fullmatch(clean_path)
    if clean_method == "POST" and match is not None:
        submission_id, action = match.groups()
        submission = repo.get_submission(submission_id) or queue.get(submission_id)
        if submission is None:
            return (404, {"error": f"Submission '{submission_id}' not found.", "code": "not_found"})

        body = payload if isinstance(payload, dict) else {}

        if action == "review":
            actor = str(body.get("actor") or "api").strip() or "api"
            try:
                queue.submit_for_review(submission, actor=actor)
            except ReviewError as exc:
                return (409, {"error": str(exc), "code": "invalid_state"})
            repo.save_submission(submission)
            if audit is not None:
                audit.record(
                    actor=actor,
                    action="submission_in_review",
                    matter_id=submission.matter_id,
                    details={"submission_id": submission.id, "state": submission.state.value},
                )
            return (200, {"submission": submission.to_dict()})

        if action == "approve":
            reviewer = body.get("reviewer")
            if not isinstance(reviewer, str) or not reviewer.strip():
                return (
                    400,
                    {"error": "Field 'reviewer' is required.", "code": "validation_error"},
                )
            clean_reviewer = reviewer.strip()
            note = str(body.get("note") or "Approved by human reviewer")
            try:
                queue.approve(submission, reviewer=clean_reviewer, note=note)
            except ReviewError as exc:
                return (409, {"error": str(exc), "code": "invalid_state"})
            repo.save_submission(submission)
            if audit is not None:
                audit.record(
                    actor=clean_reviewer,
                    action="submission_approved",
                    matter_id=submission.matter_id,
                    details={
                        "submission_id": submission.id,
                        "reviewer": clean_reviewer,
                        "state": submission.state.value,
                    },
                )
            return (200, {"submission": submission.to_dict()})

        if action == "reject":
            reviewer = body.get("reviewer")
            reason = body.get("reason")
            if (
                not isinstance(reviewer, str)
                or not reviewer.strip()
                or not isinstance(reason, str)
                or not reason.strip()
            ):
                return (
                    400,
                    {
                        "error": "Fields 'reviewer' and 'reason' are required.",
                        "code": "validation_error",
                    },
                )
            clean_reviewer = reviewer.strip()
            clean_reason = reason.strip()
            try:
                queue.reject(submission, reviewer=clean_reviewer, reason=clean_reason)
            except ReviewError as exc:
                return (409, {"error": str(exc), "code": "invalid_state"})
            repo.save_submission(submission)
            if audit is not None:
                audit.record(
                    actor=clean_reviewer,
                    action="submission_rejected",
                    matter_id=submission.matter_id,
                    details={
                        "submission_id": submission.id,
                        "reviewer": clean_reviewer,
                        "reason": clean_reason,
                        "state": submission.state.value,
                    },
                )
            return (200, {"submission": submission.to_dict()})

        if action == "submit":
            matter = repo.get_matter(submission.matter_id)
            document = repo.get_document(submission.document_id)
            if matter is None or document is None:
                return (
                    404,
                    {
                        "error": "Associated matter or document not found.",
                        "code": "not_found",
                    },
                )
            actor = str(body.get("actor") or submission.reviewer or "api").strip() or "api"
            try:
                adapter = get_authority(matter.authority)
            except UnknownAuthorityError as exc:
                return (400, {"error": str(exc), "code": "validation_error"})

            try:
                receipt = submit(submission, document, adapter, actor=actor, audit=audit)
            except SubmissionBlockedError as exc:
                return (
                    409,
                    {
                        "error": str(exc),
                        "code": "submission_blocked",
                        "state": submission.state.value,
                    },
                )

            repo.save_submission(submission)
            queue.register(submission)
            return (
                200,
                {
                    "submission": submission.to_dict(),
                    "receipt": receipt.to_dict(),
                },
            )

    return (404, {"error": f"Route '{clean_method} {clean_path}' not found.", "code": "not_found"})


def _make_handler(
    repo: SQLiteRepository,
    queue: ReviewQueue,
    audit: AuditLog,
) -> type[BaseHTTPRequestHandler]:
    class LegalEngineHTTPHandler(BaseHTTPRequestHandler):
        server_version = "LegalEngineHTTP/0.1"

        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(raw)

        def do_OPTIONS(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
            status, body = handle_api_request("GET", self.path, None, repo, queue, audit)
            self._send_json(status, body)

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
            content_length = int(self.headers.get("Content-Length") or 0)
            payload: dict[str, Any] | None = {}
            if content_length > 0:
                raw_body = self.rfile.read(content_length)
                try:
                    decoded = json.loads(raw_body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self._send_json(400, {"error": "Invalid JSON body.", "code": "invalid_json"})
                    return
                if not isinstance(decoded, dict):
                    self._send_json(
                        400, {"error": "JSON body must be an object.", "code": "validation_error"}
                    )
                    return
                payload = decoded

            status, body = handle_api_request("POST", self.path, payload, repo, queue, audit)
            self._send_json(status, body)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            # Silence default stderr noise during tests; callers can inspect audit logs.
            return

    return LegalEngineHTTPHandler


def create_server(
    host: str = "127.0.0.1",
    port: int = 8790,
    db_path: Path | str = "legal_lab.db",
    audit_path: Path | str | None = None,
) -> tuple[ThreadingHTTPServer, SQLiteRepository]:
    """Create a configured ThreadingHTTPServer and its backing SQLiteRepository."""
    resolved_audit = audit_path
    if resolved_audit is None:
        env_audit = os.environ.get("LEGAL_LAB_AUDIT_PATH")
        if env_audit:
            resolved_audit = env_audit
        elif str(db_path) != ":memory:":
            resolved_audit = Path(db_path).with_suffix(".audit.jsonl")
        else:
            resolved_audit = "audit-demo.jsonl"

    repo = SQLiteRepository(db_path)
    queue = ReviewQueue(repo.list_submissions())
    audit = AuditLog(resolved_audit)
    handler_cls = _make_handler(repo, queue, audit)
    server = ThreadingHTTPServer((host, port), handler_cls)
    return server, repo


def run_server(
    host: str = "127.0.0.1",
    port: int = 8790,
    db_path: Path | str = "legal_lab.db",
    audit_path: Path | str | None = None,
) -> None:
    """Start the pure-stdlib LegalTech API server until interrupted."""
    server, repo = create_server(host=host, port=port, db_path=db_path, audit_path=audit_path)
    bound_host, bound_port = server.server_address[:2]
    print(f"Legal Engine API listening on http://{bound_host}:{bound_port} (mode=synthetic-only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        repo.close()
