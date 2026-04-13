from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def new_id() -> str:
    return str(uuid4())


@dataclass(slots=True)
class AgentRunRecord:
    id: str
    agent_id: str
    started_at: str
    ended_at: str | None = None
    status: str = "running"
    total_steps: int = 0


@dataclass(slots=True)
class AgentEventRecord:
    id: str
    timestamp: str
    agent_id: str
    run_id: str
    event_type: str
    input_payload: Any = None
    output_payload: Any = None
    tool_name: str | None = None
    status: str = "success"
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
