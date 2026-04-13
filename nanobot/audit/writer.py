from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.audit.cleanup import build_cutoff_timestamp
from nanobot.audit.store import AuditStore
from nanobot.audit.types import AgentEventRecord, AgentRunRecord, new_id, utc_now
from nanobot.config.schema import AuditConfig

_SENTINEL = object()


class AuditWriter:
    def __init__(self, config: AuditConfig) -> None:
        self.config = config
        self.enabled = config.enabled
        self.db_path = Path(config.db_path).expanduser()
        self._store = AuditStore(self.db_path)
        self._queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=config.queue_size)
        self._start_lock = asyncio.Lock()
        self._worker_task: asyncio.Task[None] | None = None
        self._started = False
        self._last_cleanup_monotonic = 0.0

    async def ensure_started(self) -> bool:
        if not self.enabled:
            return False
        if self._started:
            return True
        async with self._start_lock:
            if self._started:
                return True
            try:
                await self._store.initialize()
                self._worker_task = asyncio.create_task(self._worker())
                self._last_cleanup_monotonic = time.monotonic()
                self._started = True
                await self._run_cleanup()
            except Exception:
                logger.exception("Failed to initialize audit writer")
                self.enabled = False
                return False
        return True

    async def shutdown(self) -> None:
        if not self._started:
            return
        try:
            await self._queue.put(_SENTINEL)
            if self._worker_task is not None:
                await self._worker_task
        except Exception:
            logger.exception("Failed to shut down audit writer cleanly")
        finally:
            await self._store.close()
            self._worker_task = None
            self._started = False

    async def start_run(self, agent_id: str) -> str | None:
        if not await self.ensure_started():
            return None
        run_id = new_id()
        self._enqueue(
            AgentRunRecord(
                id=run_id,
                agent_id=agent_id,
                started_at=utc_now(),
            )
        )
        return run_id

    async def finish_run(
        self,
        run_id: str | None,
        *,
        status: str,
        total_steps: int,
    ) -> None:
        if not run_id or not await self.ensure_started():
            return
        self._enqueue(
            {
                "type": "finish_run",
                "run_id": run_id,
                "ended_at": utc_now(),
                "status": status,
                "total_steps": total_steps,
            }
        )

    async def record_event(
        self,
        *,
        run_id: str | None,
        agent_id: str,
        event_type: str,
        input_payload: Any = None,
        output_payload: Any = None,
        tool_name: str | None = None,
        status: str = "success",
        duration_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if not run_id or not await self.ensure_started():
            return
        self._enqueue(
            AgentEventRecord(
                id=new_id(),
                timestamp=utc_now(),
                agent_id=agent_id,
                run_id=run_id,
                event_type=event_type,
                input_payload=input_payload,
                output_payload=output_payload,
                tool_name=tool_name,
                status=status,
                duration_ms=duration_ms,
                metadata=metadata or {},
            )
        )

    def _enqueue(self, item: AgentRunRecord | AgentEventRecord | dict[str, Any]) -> None:
        if not self._started:
            return
        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull:
            logger.warning("Audit queue full; dropping audit event")

    async def _worker(self) -> None:
        while True:
            item = await self._queue.get()
            if item is _SENTINEL:
                self._queue.task_done()
                break
            try:
                if isinstance(item, AgentRunRecord):
                    await self._store.insert_run(item)
                elif isinstance(item, AgentEventRecord):
                    await self._store.insert_event(item)
                elif isinstance(item, dict) and item.get("type") == "finish_run":
                    await self._store.finish_run(
                        item["run_id"],
                        ended_at=item["ended_at"],
                        status=item["status"],
                        total_steps=item["total_steps"],
                    )
                if self._should_run_cleanup():
                    await self._run_cleanup()
            except Exception:
                logger.exception("Failed to persist audit record")
            finally:
                self._queue.task_done()

    def _should_run_cleanup(self) -> bool:
        interval_s = self.config.cleanup_interval_minutes * 60
        return (time.monotonic() - self._last_cleanup_monotonic) >= interval_s

    async def _run_cleanup(self) -> None:
        try:
            await self._store.cleanup(build_cutoff_timestamp(self.config.retention_days))
            self._last_cleanup_monotonic = time.monotonic()
        except Exception:
            logger.exception("Audit cleanup failed")
