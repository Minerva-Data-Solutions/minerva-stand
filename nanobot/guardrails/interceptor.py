from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

from nanobot.audit.writer import AuditWriter
from nanobot.guardrails.loader import GuardrailsLoader
from nanobot.guardrails.types import ActionRequest
from nanobot.guardrails.validator import validate_action


@dataclass(slots=True)
class ToolExecutionOutcome:
    result: Any
    event: dict[str, str]
    error: BaseException | None


class ToolExecutionInterceptor:
    def __init__(
        self,
        *,
        workspace: Path,
        agent_id: str,
        run_id: str | None,
        audit_writer: AuditWriter | None = None,
        guardrails_loader: GuardrailsLoader | None = None,
    ) -> None:
        self.workspace = workspace
        self.agent_id = agent_id
        self.run_id = run_id
        self.audit_writer = audit_writer
        self.guardrails_loader = guardrails_loader

    async def execute(
        self,
        *,
        tool_name: str,
        params: dict[str, Any],
        invoke: Callable[[], Awaitable[Any]],
        fail_on_tool_error: bool,
        error_hint: str,
    ) -> ToolExecutionOutcome:
        started = time.perf_counter()
        validation = self._validate(tool_name, params)
        if validation is not None and not validation.allowed:
            message = f"Error: Tool call blocked by guardrails: {validation.message}"
            duration_ms = max(0, int((time.perf_counter() - started) * 1000))
            await self._record_event(
                tool_name=tool_name,
                params=params,
                result=message,
                status="fail",
                duration_ms=duration_ms,
                metadata={
                    "reason_code": validation.reason_code,
                    "matched_rule": validation.matched_rule,
                    **validation.metadata,
                },
            )
            error = RuntimeError(message) if fail_on_tool_error else None
            return ToolExecutionOutcome(
                result=message + error_hint,
                event={
                    "name": tool_name,
                    "status": "error",
                    "detail": (validation.message or "guardrails blocked the tool call")[:120],
                },
                error=error,
            )
        try:
            result = await invoke()
        except BaseException as exc:
            duration_ms = max(0, int((time.perf_counter() - started) * 1000))
            message = f"Error: {type(exc).__name__}: {exc}"
            await self._record_event(
                tool_name=tool_name,
                params=params,
                result=message,
                status="fail",
                duration_ms=duration_ms,
                metadata={},
            )
            error = exc if fail_on_tool_error else None
            return ToolExecutionOutcome(
                result=message,
                event={"name": tool_name, "status": "error", "detail": str(exc)[:120]},
                error=error,
            )
        duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        status = "success"
        detail = _summarize_result(result)
        final_result = result
        error: BaseException | None = None
        event_status = "ok"
        if isinstance(result, str) and result.startswith("Error"):
            status = "fail"
            event_status = "error"
            detail = result.replace("\n", " ").strip()[:120]
            if fail_on_tool_error:
                error = RuntimeError(result)
                final_result = result + error_hint
        await self._record_event(
            tool_name=tool_name,
            params=params,
            result=result,
            status=status,
            duration_ms=duration_ms,
            metadata={},
        )
        return ToolExecutionOutcome(
            result=final_result,
            event={"name": tool_name, "status": event_status, "detail": detail},
            error=error,
        )

    async def record_blocked(
        self,
        *,
        tool_name: str,
        params: dict[str, Any],
        message: str,
        reason_code: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if self.audit_writer is None:
            return
        await self.audit_writer.record_event(
            run_id=self.run_id,
            agent_id=self.agent_id,
            event_type="tool_call",
            input_payload=params,
            output_payload=message,
            tool_name=tool_name,
            status="fail",
            duration_ms=0,
            metadata={"reason_code": reason_code, **(metadata or {})},
        )

    def _validate(self, tool_name: str, params: dict[str, Any]):
        if self.guardrails_loader is None or not self.guardrails_loader.enabled:
            return None
        policy = self.guardrails_loader.get_policy()
        action = ActionRequest(tool_name=tool_name, params=params, workspace=self.workspace)
        return validate_action(action, policy)

    async def _record_event(
        self,
        *,
        tool_name: str,
        params: dict[str, Any],
        result: Any,
        status: str,
        duration_ms: int,
        metadata: dict[str, Any],
    ) -> None:
        if self.audit_writer is None:
            return
        await self.audit_writer.record_event(
            run_id=self.run_id,
            agent_id=self.agent_id,
            event_type="tool_call",
            input_payload=params,
            output_payload=result,
            tool_name=tool_name,
            status=status,
            duration_ms=duration_ms,
            metadata=metadata,
        )


def _summarize_result(result: Any) -> str:
    if result is None:
        return "(empty)"
    detail = str(result).replace("\n", " ").strip()
    if not detail:
        return "(empty)"
    if len(detail) > 120:
        return detail[:120] + "..."
    return detail
