"""Tamper-evident SHA-256 hash-chained append-only JSONL audit log."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading
from typing import Any

GENESIS_HASH = "0" * 64
_REQUIRED_FIELDS = frozenset(
    {"timestamp", "actor", "action", "matter_id", "details", "prev_hash", "entry_hash"}
)


def _compute_entry_hash(payload: dict[str, Any]) -> str:
    """Compute canonical SHA-256 hex digest excluding entry_hash."""
    hashable = {key: value for key, value in payload.items() if key != "entry_hash"}
    canonical = json.dumps(hashable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditLog:
    """Append-only JSONL audit log with SHA-256 prev_hash/entry_hash chaining."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()

    def _last_hash_unlocked(self) -> str:
        if not self.path.exists():
            return GENESIS_HASH
        last_line = ""
        with self.path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                stripped = raw_line.strip()
                if stripped:
                    last_line = stripped
        if not last_line:
            return GENESIS_HASH
        parsed = json.loads(last_line)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("entry_hash"), str):
            raise ValueError("Existing audit log tail is corrupted and lacks a valid entry_hash.")
        return parsed["entry_hash"]

    def record(
        self,
        actor: str,
        action: str,
        matter_id: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append a cryptographically chained audit event and return the written entry."""
        with self._lock:
            prev_hash = self._last_hash_unlocked()
            entry: dict[str, Any] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": actor,
                "action": action,
                "matter_id": matter_id,
                "details": dict(details) if details is not None else {},
                "prev_hash": prev_hash,
            }
            entry["entry_hash"] = _compute_entry_hash(entry)

            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
                handle.flush()
            return entry

    def read_entries(self) -> list[dict[str, Any]]:
        """Read all JSONL entries from disk without mutating state."""
        with self._lock:
            if not self.path.exists():
                return []
            entries: list[dict[str, Any]] = []
            with self.path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    stripped = raw_line.strip()
                    if stripped:
                        entries.append(json.loads(stripped))
            return entries

    def verify_integrity(self) -> bool:
        """Verify the full SHA-256 hash chain from GENESIS_HASH through every line."""
        with self._lock:
            if not self.path.exists():
                return True

            expected_prev_hash = GENESIS_HASH
            try:
                with self.path.open("r", encoding="utf-8") as handle:
                    for raw_line in handle:
                        stripped = raw_line.strip()
                        if not stripped:
                            continue
                        entry = json.loads(stripped)
                        if not isinstance(entry, dict):
                            return False
                        if not _REQUIRED_FIELDS.issubset(entry.keys()):
                            return False
                        if entry.get("prev_hash") != expected_prev_hash:
                            return False
                        computed = _compute_entry_hash(entry)
                        if entry.get("entry_hash") != computed:
                            return False
                        expected_prev_hash = entry["entry_hash"]
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                return False

            return True
