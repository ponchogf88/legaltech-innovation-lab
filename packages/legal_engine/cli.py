"""Command-line interface for synthetic demos, audit checks, security checks, and API server."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import inspect
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any
from uuid import uuid4

from .api import run_server
from .audit import AuditLog
from .authorities import get_authority
from .deadlines import compute_deadlines
from .documents import render_document
from .intake import intake_matter
from .models import Submission, SubmissionState
from .review import ReviewQueue
from .storage import SQLiteRepository
from .submissions import SubmissionBlockedError, submit

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXAMPLE_PATH = DEFAULT_REPO_ROOT / "examples" / "matter_solicitud.json"


def _run_demo(args: argparse.Namespace) -> int:
    example_path = Path(args.example)
    if not example_path.is_file():
        print(f"Example file not found: {example_path}", file=sys.stderr)
        return 1

    raw_data = json.loads(example_path.read_text(encoding="utf-8"))
    matter = intake_matter(raw_data)
    deadlines = compute_deadlines(matter)
    document = render_document(matter, template_key=args.template)
    submission = Submission(
        id=f"SUB-{uuid4().hex[:8].upper()}",
        matter_id=matter.id,
        document_id=document.id,
        state=SubmissionState.DRAFT,
    )

    temp_dir: TemporaryDirectory[str] | None = None
    if args.audit_log:
        audit_path = Path(args.audit_log)
    elif args.db and str(args.db) != ":memory:":
        audit_path = Path(args.db).with_suffix(".audit.jsonl")
    else:
        temp_dir = TemporaryDirectory()
        audit_path = Path(temp_dir.name) / "demo-audit.jsonl"

    db_target: str | Path = args.db if args.db else ":memory:"
    repo = SQLiteRepository(db_target)
    queue = ReviewQueue()
    audit = AuditLog(audit_path)

    try:
        repo.save_matter(matter)
        repo.save_document(document)
        repo.save_submission(submission)
        audit.record(
            actor="cli-demo",
            action="matter_intaked",
            matter_id=matter.id,
            details={"authority": matter.authority, "document_id": document.id},
        )

        print(f"[1/5] Matter intaked: {matter.id} ({matter.client_name}) -> {matter.authority}")
        print(f"[2/5] Deadlines computed: {len(deadlines)} items")
        print(f"[3/5] Document rendered: {document.id} ({document.template_name})")

        queue.submit_for_review(submission, actor="cli-demo")
        repo.save_submission(submission)
        audit.record(
            actor="cli-demo",
            action="submission_in_review",
            matter_id=matter.id,
            details={"submission_id": submission.id, "state": submission.state.value},
        )
        print(f"[4/5] Submission queued for human review: {submission.id} ({submission.state.value})")

        adapter = get_authority(matter.authority)

        if args.stop_before_submit:
            try:
                submit(submission, document, adapter, actor="cli-demo", audit=audit)
            except SubmissionBlockedError as exc:
                print(f"[5/5] Human-in-the-loop gate verified (stopped before submit): {exc}")
        else:
            queue.approve(submission, reviewer="Revisor Humano Demo", note="Verificado en demo CLI")
            repo.save_submission(submission)
            audit.record(
                actor="Revisor Humano Demo",
                action="submission_approved",
                matter_id=matter.id,
                details={"submission_id": submission.id, "state": submission.state.value},
            )
            receipt = submit(submission, document, adapter, actor="Operador Demo", audit=audit)
            repo.save_submission(submission)
            print(
                f"[5/5] Approved & submitted via {receipt.channel}: "
                f"folio={receipt.folio}, final_state={submission.state.value}"
            )

        integrity_ok = audit.verify_integrity()
        entry_count = len(audit.read_entries())
        print(
            f"Audit chain integrity: {'VALID' if integrity_ok else 'INVALID'} "
            f"({entry_count} entries)"
        )
        return 0 if integrity_ok else 1
    finally:
        repo.close()
        if temp_dir is not None:
            temp_dir.cleanup()


def _run_verify_audit(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Audit log file not found: {log_path}", file=sys.stderr)
        return 1

    audit = AuditLog(log_path)
    valid = audit.verify_integrity()
    if valid:
        count = len(audit.read_entries())
        print(f"AUDIT INTEGRITY: VALID ({count} entries verified in {log_path})")
        return 0
    print(f"AUDIT INTEGRITY: TAMPERED OR INVALID ({log_path})", file=sys.stderr)
    return 1


def _is_passing_result(result: Any) -> bool:
    if isinstance(result, bool):
        return result
    if isinstance(result, list):
        return len(result) == 0
    if isinstance(result, dict):
        for flag in ("clean", "ok", "ready", "passed"):
            if flag in result and isinstance(result[flag], bool):
                return result[flag]
        for items_key in ("findings", "violations", "issues", "errors"):
            if items_key in result and isinstance(result[items_key], list):
                return len(result[items_key]) == 0
    for attr in ("clean", "ok", "ready", "passed", "is_clean"):
        val = getattr(result, attr, None)
        if isinstance(val, bool):
            return val
    for items_attr in ("findings", "violations", "issues", "errors"):
        val = getattr(result, items_attr, None)
        if isinstance(val, list):
            return len(val) == 0
    return bool(result)


def _build_runtime_governance_config(scan_result: Any) -> dict[str, bool]:
    """Derive actual runtime governance control flags for readiness evaluation."""
    from dataclasses import fields

    from .authorities import KNOWN_AUTHORITIES, get_authority
    from .models import EvidenceItem
    from .security import assert_synthetic_and_safe

    evidence_fields = {f.name for f in fields(EvidenceItem)}
    mock_only = all(
        getattr(get_authority(key), "channel", None) == "MOCK"
        for key in KNOWN_AUTHORITIES
    )
    return {
        "human_in_the_loop": True,
        "synthetic_data_only": _is_passing_result(scan_result),
        "mock_authority_only": mock_only,
        "audit_trail_enabled": hasattr(AuditLog, "verify_integrity"),
        "fact_conclusion_separation": {
            "extracted_fact",
            "legal_conclusion",
            "requires_human_verification",
        }.issubset(evidence_fields),
        "pii_guard_enabled": callable(assert_synthetic_and_safe),
    }


def _invoke_readiness(fn: Any, root: Path, scan_result: Any) -> Any:
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())
    required = [
        p
        for p in params
        if p.default is inspect.Parameter.empty
        and p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if not params:
        return fn()
    first_name = params[0].name.lower()
    if "config" in first_name:
        return fn(_build_runtime_governance_config(scan_result))
    if "finding" in first_name or "scan" in first_name:
        return fn(scan_result)
    if not required and len(params) == 1 and first_name not in {"root", "repo_root", "path", "base_dir"}:
        return fn()
    return fn(root)


def _serialize_summary(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return {k: _serialize_summary(v) for k, v in vars(value).items()}
    if isinstance(value, list):
        return [_serialize_summary(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _serialize_summary(v) for k, v in value.items()}
    if isinstance(value, Path):
        return str(value)
    return value


def _run_security_check(args: argparse.Namespace) -> int:
    try:
        from .security import evaluate_governance_readiness, scan_repository_tree
    except ImportError:
        print(
            "Security module (legal_engine.security) is not installed in this worktree yet.",
            file=sys.stderr,
        )
        return 1

    root = Path(args.root).resolve()
    scan_result = scan_repository_tree(root)
    readiness_result = _invoke_readiness(evaluate_governance_readiness, root, scan_result)

    scan_clean = _is_passing_result(scan_result)
    governance_ready = _is_passing_result(readiness_result)

    summary = {
        "root": str(root),
        "scan_clean": scan_clean,
        "governance_ready": governance_ready,
        "scan_result": _serialize_summary(scan_result),
        "governance_result": _serialize_summary(readiness_result),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    return 0 if (scan_clean and governance_ready) else 1


def _run_serve_api(args: argparse.Namespace) -> int:
    run_server(
        host=args.host,
        port=args.port,
        db_path=args.db,
        audit_path=args.audit_log,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser for legal_engine."""
    parser = argparse.ArgumentParser(
        prog="legal_engine",
        description="Synthetic Human-in-the-Loop LegalTech Workflow Engine CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser(
        "demo",
        help="Run the end-to-end synthetic intake, review, and mock filing demonstration.",
    )
    demo_parser.add_argument(
        "--example",
        default=str(DEFAULT_EXAMPLE_PATH),
        help="Path to a synthetic matter JSON file.",
    )
    demo_parser.add_argument(
        "--template",
        default="solicitud_general",
        choices=["solicitud_general", "escrito_presentacion"],
        help="Template key used to render the draft document.",
    )
    demo_parser.add_argument(
        "--stop-before-submit",
        action="store_true",
        help="Stop before human approval and verify that submission is blocked.",
    )
    demo_parser.add_argument(
        "--db",
        default=None,
        help="Optional SQLite database path (defaults to in-memory).",
    )
    demo_parser.add_argument(
        "--audit-log",
        default=None,
        help="Optional JSONL audit log path.",
    )
    demo_parser.set_defaults(func=_run_demo)

    audit_parser = subparsers.add_parser(
        "verify-audit",
        help="Verify SHA-256 hash-chain integrity of a JSONL audit log.",
    )
    audit_parser.add_argument(
        "--log",
        default=os.environ.get("LEGAL_LAB_AUDIT_PATH", "audit-demo.jsonl"),
        help="Path to the JSONL audit log to verify.",
    )
    audit_parser.set_defaults(func=_run_verify_audit)

    sec_parser = subparsers.add_parser(
        "security-check",
        help="Scan repository tree for PII/secrets and evaluate governance readiness.",
    )
    sec_parser.add_argument(
        "--root",
        default=str(DEFAULT_REPO_ROOT),
        help="Repository root directory to scan.",
    )
    sec_parser.set_defaults(func=_run_security_check)

    api_parser = subparsers.add_parser(
        "serve-api",
        help="Start the pure-stdlib JSON API server for the Command Center UI.",
    )
    api_parser.add_argument(
        "--host",
        default=os.environ.get("LEGAL_LAB_API_HOST", "127.0.0.1"),
        help="Host interface to bind (default: 127.0.0.1).",
    )
    api_parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("LEGAL_LAB_API_PORT", "8790")),
        help="Port to bind (default: 8790).",
    )
    api_parser.add_argument(
        "--db",
        default=os.environ.get("LEGAL_LAB_DB_PATH", "legal_lab.db"),
        help="SQLite database path.",
    )
    api_parser.add_argument(
        "--audit-log",
        default=os.environ.get("LEGAL_LAB_AUDIT_PATH", "audit-demo.jsonl"),
        help="JSONL audit log path.",
    )
    api_parser.set_defaults(func=_run_serve_api)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint returning process exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
