from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from rich.table import Table
from rich.text import Text


def query_runs(
    db_path: Path,
    *,
    limit: int = 20,
    status: str | None = None,
    agent_id: str | None = None,
) -> list[sqlite3.Row]:
    clauses: list[str] = []
    params: list[object] = []
    if status:
        clauses.append("status = ?")
        params.append(status)
    if agent_id:
        clauses.append("agent_id = ?")
        params.append(agent_id)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        "SELECT id, agent_id, started_at, ended_at, status, total_steps "
        f"FROM agent_runs {where_sql} "
        "ORDER BY started_at DESC LIMIT ?"
    )
    params.append(limit)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return rows


def query_events(
    db_path: Path,
    *,
    limit: int = 50,
    run_id: str | None = None,
    event_type: str | None = None,
    tool_name: str | None = None,
    status: str | None = None,
) -> list[sqlite3.Row]:
    clauses: list[str] = []
    params: list[object] = []
    if run_id:
        clauses.append("run_id = ?")
        params.append(run_id)
    if event_type:
        clauses.append("event_type = ?")
        params.append(event_type)
    if tool_name:
        clauses.append("tool_name = ?")
        params.append(tool_name)
    if status:
        clauses.append("status = ?")
        params.append(status)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        "SELECT timestamp, run_id, event_type, tool_name, status, duration_ms, input, output, metadata_json "
        f"FROM agent_events {where_sql} "
        "ORDER BY timestamp DESC LIMIT ?"
    )
    params.append(limit)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return rows


def build_runs_table(rows: list[sqlite3.Row]) -> Table:
    table = Table(title="Agent Runs")
    table.add_column("Run ID", overflow="fold")
    table.add_column("Agent ID", overflow="fold")
    table.add_column("Status")
    table.add_column("Started At")
    table.add_column("Ended At")
    table.add_column("Steps", justify="right")
    for row in rows:
        table.add_row(
            row["id"],
            row["agent_id"],
            row["status"],
            row["started_at"],
            row["ended_at"] or "-",
            str(row["total_steps"]),
        )
    return table


def build_events_table(rows: list[sqlite3.Row]) -> Table:
    table = Table(title="Agent Logs")
    table.add_column("Timestamp")
    table.add_column("Run ID", overflow="fold")
    table.add_column("Type")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Duration", justify="right")
    table.add_column("Input", overflow="fold")
    table.add_column("Output", overflow="fold")
    for row in rows:
        table.add_row(
            row["timestamp"],
            row["run_id"],
            row["event_type"],
            row["tool_name"] or "-",
            row["status"],
            f"{row['duration_ms']} ms" if row["duration_ms"] is not None else "-",
            _format_cell(row["input"]),
            _format_cell(row["output"]),
        )
    return table


def build_empty_text(label: str) -> Text:
    return Text(f"No {label} found.")


def _format_cell(value: str | None, limit: int = 120) -> str:
    if not value:
        return "-"
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        text = value
    else:
        text = json.dumps(parsed, ensure_ascii=False)
    text = text.replace("\n", " ")
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text
