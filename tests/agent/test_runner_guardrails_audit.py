from __future__ import annotations

import sqlite3
from unittest.mock import AsyncMock, MagicMock

import pytest

from nanobot.agent.runner import AgentRunner, AgentRunSpec
from nanobot.audit.writer import AuditWriter
from nanobot.config.schema import AgentDefaults, AuditConfig, GuardrailsConfig
from nanobot.guardrails.interceptor import ToolExecutionInterceptor
from nanobot.guardrails.loader import GuardrailsLoader
from nanobot.providers.base import LLMResponse, ToolCallRequest

_MAX_TOOL_RESULT_CHARS = AgentDefaults().max_tool_result_chars


@pytest.mark.asyncio
async def test_runner_interceptor_blocks_guardrailed_tool_and_audits_attempt(tmp_path):
    db_path = tmp_path / "agent_audit.db"
    writer = AuditWriter(AuditConfig(enabled=True, db_path=str(db_path)))
    run_id = await writer.start_run("agent-1")

    provider = MagicMock()
    provider.chat_with_retry = AsyncMock(
        side_effect=[
            LLMResponse(
                content="working",
                tool_calls=[
                    ToolCallRequest(id="call_1", name="exec", arguments={"command": "rm -rf /tmp/demo"})
                ],
                usage={},
            ),
            LLMResponse(content="done", tool_calls=[], usage={}),
        ]
    )
    tools = MagicMock()
    tools.get_definitions.return_value = []
    tools.execute = AsyncMock(return_value="should-not-run")

    interceptor = ToolExecutionInterceptor(
        workspace=tmp_path,
        agent_id="agent-1",
        run_id=run_id,
        audit_writer=writer,
        guardrails_loader=GuardrailsLoader(
            GuardrailsConfig(enabled=True, policy_path=str(tmp_path / "missing-policy.json"))
        ),
    )

    runner = AgentRunner(provider)
    result = await runner.run(AgentRunSpec(
        initial_messages=[],
        tools=tools,
        model="test-model",
        max_iterations=2,
        max_tool_result_chars=_MAX_TOOL_RESULT_CHARS,
        tool_interceptor=interceptor,
    ))
    await writer.finish_run(run_id, status=result.stop_reason, total_steps=1)
    await writer.shutdown()

    assert result.final_content == "done"
    assert result.tool_events[0]["status"] == "error"
    tools.execute.assert_not_awaited()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT tool_name, status, output FROM agent_events WHERE run_id = ?",
            (run_id,),
        ).fetchone()

    assert row[0] == "exec"
    assert row[1] == "fail"
    assert "blocked by guardrails" in row[2]


@pytest.mark.asyncio
async def test_runner_interceptor_audits_successful_tool_execution(tmp_path):
    db_path = tmp_path / "agent_audit.db"
    writer = AuditWriter(AuditConfig(enabled=True, db_path=str(db_path)))
    run_id = await writer.start_run("agent-1")

    provider = MagicMock()
    provider.chat_with_retry = AsyncMock(
        side_effect=[
            LLMResponse(
                content="working",
                tool_calls=[
                    ToolCallRequest(id="call_1", name="list_dir", arguments={"path": "."})
                ],
                usage={},
            ),
            LLMResponse(content="done", tool_calls=[], usage={}),
        ]
    )
    tools = MagicMock()
    tools.get_definitions.return_value = []
    tools.execute = AsyncMock(return_value="tool result")

    interceptor = ToolExecutionInterceptor(
        workspace=tmp_path,
        agent_id="agent-1",
        run_id=run_id,
        audit_writer=writer,
        guardrails_loader=GuardrailsLoader(
            GuardrailsConfig(enabled=True, policy_path=str(tmp_path / "missing-policy.json"))
        ),
    )

    runner = AgentRunner(provider)
    result = await runner.run(AgentRunSpec(
        initial_messages=[],
        tools=tools,
        model="test-model",
        max_iterations=2,
        max_tool_result_chars=_MAX_TOOL_RESULT_CHARS,
        tool_interceptor=interceptor,
    ))
    await writer.finish_run(run_id, status=result.stop_reason, total_steps=1)
    await writer.shutdown()

    assert result.final_content == "done"
    assert result.tool_events == [{"name": "list_dir", "status": "ok", "detail": "tool result"}]
    tools.execute.assert_awaited_once()

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT tool_name, status, output FROM agent_events WHERE run_id = ?",
            (run_id,),
        ).fetchone()

    assert row[0] == "list_dir"
    assert row[1] == "success"
    assert row[2] == "tool result"
