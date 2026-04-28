"""Subagent prompts must include the GUARDRAIL block as the last section."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from nanobot.agent.subagent import SubagentManager
from nanobot.bus.queue import MessageBus


def _make_manager(workspace: Path) -> SubagentManager:
    provider = MagicMock()
    provider.get_default_model.return_value = "test-model"
    return SubagentManager(
        provider=provider,
        workspace=workspace,
        bus=MessageBus(),
        max_tool_result_chars=4096,
    )


def test_subagent_prompt_includes_guardrail_block(tmp_path: Path) -> None:
    (tmp_path / "GUARDRAIL.md").write_text("SUB-MARKER-XYZ\n", encoding="utf-8")
    mgr = _make_manager(tmp_path)

    prompt = mgr._build_subagent_prompt()

    assert "GUARDRAIL — non-negotiable safety policy" in prompt
    assert "<guardrails>" in prompt
    assert "SUB-MARKER-XYZ" in prompt
    assert "</guardrails>" in prompt


def test_subagent_prompt_uses_bundled_guardrail_when_workspace_missing(tmp_path: Path) -> None:
    """Even with no workspace GUARDRAIL.md, sub-agent must inherit safety rules."""
    mgr = _make_manager(tmp_path)

    prompt = mgr._build_subagent_prompt()

    assert "GUARDRAIL — non-negotiable safety policy" in prompt
    assert "<guardrails>" in prompt


def test_subagent_prompt_guardrail_is_last_block(tmp_path: Path) -> None:
    (tmp_path / "GUARDRAIL.md").write_text("LAST-RULE", encoding="utf-8")
    mgr = _make_manager(tmp_path)

    prompt = mgr._build_subagent_prompt()
    last_section = prompt.rsplit("---", 1)[-1]

    assert "GUARDRAIL — non-negotiable safety policy" in last_section
    assert "LAST-RULE" in last_section
