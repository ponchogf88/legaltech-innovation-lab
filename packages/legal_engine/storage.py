"""SQLite persistence repository for synthetic matters, documents, submissions, and evidence."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime
import json
from pathlib import Path
import sqlite3
import threading

from .models import Document, EvidenceItem, Matter, Submission, SubmissionState

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS matters (
    id TEXT PRIMARY KEY,
    client_name TEXT NOT NULL,
    matter_type TEXT NOT NULL,
    authority TEXT NOT NULL,
    facts TEXT NOT NULL,
    documents_needed TEXT NOT NULL,
    filing_date TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    matter_id TEXT NOT NULL,
    template_name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    matter_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    state TEXT NOT NULL,
    receipt_folio TEXT,
    reviewer TEXT,
    rejection_reason TEXT,
    history TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_items (
    id TEXT PRIMARY KEY,
    matter_id TEXT NOT NULL,
    title TEXT NOT NULL,
    kind TEXT NOT NULL,
    source_pages TEXT NOT NULL,
    extracted_fact TEXT NOT NULL,
    legal_conclusion TEXT NOT NULL,
    requires_human_verification INTEGER NOT NULL,
    verification_note TEXT NOT NULL
);
"""


class SQLiteRepository:
    """Thread-safe SQLite repository with context-managed transactions."""

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        self._raw_path = str(db_path)
        self._is_memory = self._raw_path == ":memory:" or self._raw_path.startswith("file::memory:")
        self._lock = threading.RLock()

        if not self._is_memory:
            Path(self._raw_path).parent.mkdir(parents=True, exist_ok=True)

        self._conn: sqlite3.Connection | None = sqlite3.connect(
            self._raw_path,
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        if not self._is_memory:
            self._conn.execute("PRAGMA journal_mode = WAL")

        with self._connect() as conn:
            conn.executescript(_SCHEMA_SQL)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            if self._conn is None:
                raise sqlite3.ProgrammingError("Cannot operate on a closed SQLiteRepository.")
            with self._conn:
                yield self._conn

    def __enter__(self) -> SQLiteRepository:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying SQLite connection cleanly."""
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    # ------------------------------------------------------------------
    # Matters
    # ------------------------------------------------------------------
    def save_matter(self, matter: Matter) -> Matter:
        """Insert or update a Matter record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO matters (
                    id, client_name, matter_type, authority, facts,
                    documents_needed, filing_date, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    client_name = excluded.client_name,
                    matter_type = excluded.matter_type,
                    authority = excluded.authority,
                    facts = excluded.facts,
                    documents_needed = excluded.documents_needed,
                    filing_date = excluded.filing_date,
                    created_at = excluded.created_at
                """,
                (
                    matter.id,
                    matter.client_name,
                    matter.matter_type,
                    matter.authority,
                    matter.facts,
                    json.dumps(matter.documents_needed, ensure_ascii=False),
                    matter.filing_date.isoformat() if matter.filing_date else None,
                    matter.created_at.isoformat(),
                ),
            )
        return matter

    def _row_to_matter(self, row: sqlite3.Row) -> Matter:
        return Matter(
            id=row["id"],
            client_name=row["client_name"],
            matter_type=row["matter_type"],
            authority=row["authority"],
            facts=row["facts"],
            documents_needed=json.loads(row["documents_needed"]),
            filing_date=date.fromisoformat(row["filing_date"]) if row["filing_date"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_matter(self, matter_id: str) -> Matter | None:
        """Fetch a Matter by ID or return None."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM matters WHERE id = ?", (matter_id,)).fetchone()
        return self._row_to_matter(row) if row is not None else None

    def list_matters(self) -> list[Matter]:
        """Return all stored matters in creation order."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM matters ORDER BY rowid ASC").fetchall()
        return [self._row_to_matter(row) for row in rows]

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------
    def save_document(self, document: Document) -> Document:
        """Insert or update a rendered Document record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, matter_id, template_name, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    matter_id = excluded.matter_id,
                    template_name = excluded.template_name,
                    content = excluded.content,
                    created_at = excluded.created_at
                """,
                (
                    document.id,
                    document.matter_id,
                    document.template_name,
                    document.content,
                    document.created_at.isoformat(),
                ),
            )
        return document

    def _row_to_document(self, row: sqlite3.Row) -> Document:
        return Document(
            id=row["id"],
            matter_id=row["matter_id"],
            template_name=row["template_name"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_document(self, document_id: str) -> Document | None:
        """Fetch a Document by ID or return None."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return self._row_to_document(row) if row is not None else None

    def list_documents(self, matter_id: str | None = None) -> list[Document]:
        """Return documents, optionally filtered by matter_id."""
        with self._connect() as conn:
            if matter_id is not None:
                rows = conn.execute(
                    "SELECT * FROM documents WHERE matter_id = ? ORDER BY rowid ASC",
                    (matter_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM documents ORDER BY rowid ASC").fetchall()
        return [self._row_to_document(row) for row in rows]

    # ------------------------------------------------------------------
    # Submissions
    # ------------------------------------------------------------------
    def save_submission(self, submission: Submission) -> Submission:
        """Insert or update a Submission record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO submissions (
                    id, matter_id, document_id, state, receipt_folio,
                    reviewer, rejection_reason, history
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    matter_id = excluded.matter_id,
                    document_id = excluded.document_id,
                    state = excluded.state,
                    receipt_folio = excluded.receipt_folio,
                    reviewer = excluded.reviewer,
                    rejection_reason = excluded.rejection_reason,
                    history = excluded.history
                """,
                (
                    submission.id,
                    submission.matter_id,
                    submission.document_id,
                    submission.state.value,
                    submission.receipt_folio,
                    submission.reviewer,
                    submission.rejection_reason,
                    json.dumps(submission.history, ensure_ascii=False),
                ),
            )
        return submission

    def _row_to_submission(self, row: sqlite3.Row) -> Submission:
        return Submission(
            id=row["id"],
            matter_id=row["matter_id"],
            document_id=row["document_id"],
            state=SubmissionState(row["state"]),
            receipt_folio=row["receipt_folio"],
            reviewer=row["reviewer"],
            rejection_reason=row["rejection_reason"],
            history=json.loads(row["history"]),
        )

    def get_submission(self, submission_id: str) -> Submission | None:
        """Fetch a Submission by ID or return None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM submissions WHERE id = ?", (submission_id,)
            ).fetchone()
        return self._row_to_submission(row) if row is not None else None

    def list_submissions(self) -> list[Submission]:
        """Return all submissions in creation order."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM submissions ORDER BY rowid ASC").fetchall()
        return [self._row_to_submission(row) for row in rows]

    # ------------------------------------------------------------------
    # Evidence Items
    # ------------------------------------------------------------------
    def save_evidence(self, evidence: EvidenceItem) -> EvidenceItem:
        """Insert or update an EvidenceItem record."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO evidence_items (
                    id, matter_id, title, kind, source_pages, extracted_fact,
                    legal_conclusion, requires_human_verification, verification_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    matter_id = excluded.matter_id,
                    title = excluded.title,
                    kind = excluded.kind,
                    source_pages = excluded.source_pages,
                    extracted_fact = excluded.extracted_fact,
                    legal_conclusion = excluded.legal_conclusion,
                    requires_human_verification = excluded.requires_human_verification,
                    verification_note = excluded.verification_note
                """,
                (
                    evidence.id,
                    evidence.matter_id,
                    evidence.title,
                    evidence.kind,
                    json.dumps(evidence.source_pages, ensure_ascii=False),
                    evidence.extracted_fact,
                    evidence.legal_conclusion,
                    1 if evidence.requires_human_verification else 0,
                    evidence.verification_note,
                ),
            )
        return evidence

    def _row_to_evidence(self, row: sqlite3.Row) -> EvidenceItem:
        return EvidenceItem(
            id=row["id"],
            matter_id=row["matter_id"],
            title=row["title"],
            kind=row["kind"],
            source_pages=json.loads(row["source_pages"]),
            extracted_fact=row["extracted_fact"],
            legal_conclusion=row["legal_conclusion"],
            requires_human_verification=bool(row["requires_human_verification"]),
            verification_note=row["verification_note"],
        )

    def list_evidence(self, matter_id: str | None = None) -> list[EvidenceItem]:
        """Return evidence items, optionally filtered by matter_id."""
        with self._connect() as conn:
            if matter_id is not None:
                rows = conn.execute(
                    "SELECT * FROM evidence_items WHERE matter_id = ? ORDER BY rowid ASC",
                    (matter_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM evidence_items ORDER BY rowid ASC").fetchall()
        return [self._row_to_evidence(row) for row in rows]
