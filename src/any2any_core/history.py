"""History store: append-only SQLite log of Results (ADR-004). No file contents."""

from __future__ import annotations

import json
from pathlib import Path

from platformdirs import user_data_path

from .models import Result


def history_path() -> Path:
    return user_data_path("any2any", appauthor=False) / "history.db"


class HistoryStore:
    def __init__(self, path: Path | None = None):
        self.path = path or history_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        import sqlite3

        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                item_id TEXT,
                status TEXT,
                source TEXT,
                output TEXT,
                plan_summary TEXT,
                warnings TEXT,
                error_code TEXT,
                duration_ms INTEGER,
                bytes_in INTEGER,
                bytes_out INTEGER
            )
            """
        )
        self._conn.commit()

    def append(self, result: Result) -> None:
        from .models import utcnow

        plan_sum = None
        if result.plan_used:
            plan_sum = json.dumps(result.plan_used.to_dict(), ensure_ascii=False)
        self._conn.execute(
            "INSERT INTO history (ts, item_id, status, source, output, plan_summary, warnings, error_code, duration_ms, bytes_in, bytes_out)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                utcnow().isoformat(),
                result.item_id,
                result.status,
                str(result.source),
                str(result.output) if result.output else None,
                plan_sum,
                json.dumps([w.to_dict() for w in result.warnings], ensure_ascii=False),
                result.error.code if result.error else None,
                result.duration_ms,
                result.bytes_in,
                result.bytes_out if result.bytes_out is not None else -1,
            ),
        )
        self._conn.commit()

    def list(self, limit: int = 20) -> list[dict]:
        cur = self._conn.execute(
            "SELECT ts, item_id, status, source, output, error_code, duration_ms FROM history ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        cols = ["ts", "item_id", "status", "source", "output", "error_code", "duration_ms"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def clear(self) -> int:
        cur = self._conn.execute("DELETE FROM history")
        self._conn.commit()
        return cur.rowcount

    def size(self) -> int:
        cur = self._conn.execute("SELECT COUNT(*) FROM history")
        return int(cur.fetchone()[0])

    def close(self) -> None:
        self._conn.close()
