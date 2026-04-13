from __future__ import annotations

import time
from typing import Any

from nanobot.agent.hook import AgentHook, AgentHookContext
from nanobot.audit.writer import AuditWriter


class AuditHook(AgentHook):
    def __init__(
        self,
        *,
        writer: AuditWriter,
        agent_id: str,
        run_id: str,
    ) -> None:
        super().__init__()
        self._writer = writer
        self._agent_id = agent_id
        self._run_id = run_id
        self._iteration_started: dict[int, float] = {}
        self.total_steps = 0

    async def before_iteration(self, context: AgentHookContext) -> None:
        self.total_steps = max(self.total_steps, context.iteration + 1)
        self._iteration_started[context.iteration] = time.perf_counter()

    async def after_iteration(self, context: AgentHookContext) -> None:
        started = self._iteration_started.pop(context.iteration, time.perf_counter())
        duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        event_type = "thought"
        status = "success"
        output_payload: Any = context.final_content or (
            context.response.content if context.response else None
        )
        metadata: dict[str, Any] = {
            "iteration": context.iteration,
            "usage": dict(context.usage or {}),
            "tool_events": list(context.tool_events or []),
            "stop_reason": context.stop_reason,
        }
        if context.tool_calls:
            event_type = "action"
            output_payload = {
                "tool_calls": [tc.to_openai_tool_call() for tc in context.tool_calls],
                "tool_events": list(context.tool_events or []),
                "final_content": context.final_content,
            }
            if any(event.get("status") == "error" for event in context.tool_events):
                status = "fail"
        if context.error:
            event_type = "error"
            status = "fail"
            output_payload = context.error
        await self._writer.record_event(
            run_id=self._run_id,
            agent_id=self._agent_id,
            event_type=event_type,
            input_payload=_build_input_payload(context.messages),
            output_payload=output_payload,
            status=status,
            duration_ms=duration_ms,
            metadata=metadata,
        )


def _build_input_payload(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not messages:
        return []
    tail = messages[-2:]
    items: list[dict[str, Any]] = []
    for item in tail:
        items.append(
            {
                "role": item.get("role"),
                "content": item.get("content"),
                "name": item.get("name"),
            }
        )
    return items
