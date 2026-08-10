"""Persistent local spool for offline buffering.

Records are appended as JSON-lines to ``queue.jsonl``. When the server is
reachable the agent drains the spool; any records that fail are re-appended
so nothing is lost during an outage.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path


class Spool:
    def __init__(self, directory: str, max_mb: int = 512):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "queue.jsonl"
        self.max_bytes = max_mb * 1024 * 1024
        self._lock = threading.Lock()

    @property
    def size_bytes(self) -> int:
        try:
            return self.path.stat().st_size
        except FileNotFoundError:
            return 0

    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    def append(self, records: list[dict]) -> int:
        if not records:
            return 0
        with self._lock:
            if self.size_bytes + len(json.dumps(records, default=str)) > self.max_bytes:
                return 0  # spool full: drop-newest, keep oldest evidence
            with self.path.open("a", encoding="utf-8") as fh:
                for record in records:
                    fh.write(json.dumps(record, default=str) + "\n")
            return len(records)

    def drain(self) -> list[dict]:
        """Return all spooled records and clear the file."""
        with self._lock:
            if not self.path.exists():
                return []
            records: list[dict] = []
            with self.path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            self.path.unlink(missing_ok=True)
            return records
