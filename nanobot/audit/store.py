from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite

from nanobot.audit.types import AgentEventRecord, AgentRunRecord


class AuditStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path).expanduser()
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        if self._conn is not None:
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA synchronous=NORMAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        await conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS agent_runs (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                status TEXT NOT NULL,
                total_steps INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS agent_events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                input TEXT,
                output TEXT,
                tool_name TEXT,
                status TEXT NOT NULL,
                duration_ms INTEGER,
                metadata_json TEXT,
                FOREIGN KEY(run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_agent_runs_started_at ON agent_runs(started_at);
            CREATE INDEX IF NOT EXISTS idx_agent_events_timestamp ON agent_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_agent_events_run_id ON agent_events(run_id);
            CREATE INDEX IF NOT EXISTS idx_agent_events_agent_id ON agent_events(agent_id);
            """
        )
        await conn.commit()
        self._conn = conn

    async def close(self) -> None:
        if self._conn is None:
            return
        await self._conn.close()
        self._conn = None

    async def insert_run(self, record: AgentRunRecord) -> None:
        conn = self._require_connection()
        await conn.execute(
            """
            INSERT INTO agent_runs (id, agent_id, started_at, ended_at, status, total_steps)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.agent_id,
                record.started_at,
                record.ended_at,
                record.status,
                record.total_steps,
            ),
        )
        await conn.commit()

    async def finish_run(
        self,
        run_id: str,
        ended_at: str,
        status: str,
        total_steps: int,
    ) -> None:
        conn = self._require_connection()
        await conn.execute(
            """
            UPDATE agent_runs
            SET ended_at = ?, status = ?, total_steps = ?
            WHERE id = ?
            """,
            (ended_at, status, total_steps, run_id),
        )
        await conn.commit()

    async def insert_event(self, record: AgentEventRecord) -> None:
        conn = self._require_connection()
        await conn.execute(
            """
            INSERT INTO agent_events (
                id, timestamp, agent_id, run_id, event_type, input, output,
                tool_name, status, duration_ms, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.timestamp,
                record.agent_id,
                record.run_id,
                record.event_type,
                _serialize_payload(record.input_payload),
                _serialize_payload(record.output_payload),
                record.tool_name,
                record.status,
                record.duration_ms,
                _serialize_payload(record.metadata),
            ),
        )
        await conn.commit()

    async def cleanup(self, cutoff_timestamp: str) -> dict[str, int]:
        conn = self._require_connection()
        event_cursor = await conn.execute(
            "DELETE FROM agent_events WHERE timestamp < ?",
            (cutoff_timestamp,),
        )
        run_cursor = await conn.execute(
            "DELETE FROM agent_runs WHERE COALESCE(ended_at, started_at) < ?",
            (cutoff_timestamp,),
        )
        await conn.commit()
        return {
            "events_deleted": event_cursor.rowcount or 0,
            "runs_deleted": run_cursor.rowcount or 0,
        }

    def _require_connection(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("AuditStore is not initialized")
        return self._conn


def _serialize_payload(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)
