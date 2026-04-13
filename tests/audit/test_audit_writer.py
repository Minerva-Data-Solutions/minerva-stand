from __future__ import annotations

import sqlite3

import pytest

from nanobot.audit.writer import AuditWriter
from nanobot.config.schema import AuditConfig


@pytest.mark.asyncio
async def test_audit_writer_persists_runs_and_events(tmp_path):
    db_path = tmp_path / "agent_audit.db"
    writer = AuditWriter(AuditConfig(enabled=True, db_path=str(db_path)))

    run_id = await writer.start_run("agent-1")
    assert run_id is not None

    await writer.record_event(
        run_id=run_id,
        agent_id="agent-1",
        event_type="tool_call",
        input_payload={"command": "ls"},
        output_payload="ok",
        tool_name="exec",
        status="success",
        duration_ms=12,
        metadata={"source": "test"},
    )
    await writer.finish_run(run_id, status="completed", total_steps=2)
    await writer.shutdown()

    with sqlite3.connect(db_path) as conn:
        run_row = conn.execute(
            "SELECT agent_id, status, total_steps FROM agent_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        event_row = conn.execute(
            "SELECT event_type, tool_name, status, duration_ms FROM agent_events WHERE run_id = ?",
            (run_id,),
        ).fetchone()

    assert run_row == ("agent-1", "completed", 2)
    assert event_row == ("tool_call", "exec", "success", 12)


@pytest.mark.asyncio
async def test_audit_writer_cleanup_removes_expired_rows(tmp_path):
    db_path = tmp_path / "agent_audit.db"
    writer = AuditWriter(AuditConfig(
        enabled=True,
        db_path=str(db_path),
        retention_days=1,
        cleanup_interval_minutes=60,
    ))

    run_id = await writer.start_run("agent-1")
    assert run_id is not None
    await writer.record_event(
        run_id=run_id,
        agent_id="agent-1",
        event_type="tool_call",
        input_payload={"command": "ls"},
        output_payload="ok",
        tool_name="exec",
        status="success",
        duration_ms=10,
    )
    await writer.finish_run(run_id, status="completed", total_steps=1)
    await writer.shutdown()

    old_timestamp = "2000-01-01T00:00:00+00:00"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE agent_runs SET started_at = ?, ended_at = ? WHERE id = ?",
            (old_timestamp, old_timestamp, run_id),
        )
        conn.execute(
            "UPDATE agent_events SET timestamp = ? WHERE run_id = ?",
            (old_timestamp, run_id),
        )
        conn.commit()

    writer = AuditWriter(AuditConfig(enabled=True, db_path=str(db_path), retention_days=1))
    await writer.ensure_started()
    await writer._run_cleanup()
    await writer.shutdown()

    with sqlite3.connect(db_path) as conn:
        run_count = conn.execute("SELECT COUNT(*) FROM agent_runs").fetchone()[0]
        event_count = conn.execute("SELECT COUNT(*) FROM agent_events").fetchone()[0]

    assert run_count == 0
    assert event_count == 0
