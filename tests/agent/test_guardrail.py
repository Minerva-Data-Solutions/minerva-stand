"""Tests for GUARDRAIL.md loading and prompt anchoring."""

from __future__ import annotations

from pathlib import Path

from nanobot.agent.context import (
    ContextBuilder,
    format_guardrail_block,
    load_guardrail,
)


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True)
    return workspace


def test_load_guardrail_prefers_workspace_file(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    (workspace / "GUARDRAIL.md").write_text("CUSTOM-RULES\n", encoding="utf-8")

    content = load_guardrail(workspace)

    assert content == "CUSTOM-RULES"


def test_load_guardrail_falls_back_to_bundled_template(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)

    content = load_guardrail(workspace)

    assert content, "should fall back to bundled GUARDRAIL.md when workspace copy is missing"
    assert "GUARDRAIL" in content


def test_format_guardrail_block_returns_empty_for_blank_input() -> None:
    assert format_guardrail_block("") == ""
    assert format_guardrail_block("   \n\n") == ""


def test_format_guardrail_block_wraps_with_supersede_preamble() -> None:
    block = format_guardrail_block("rule one")

    assert "GUARDRAIL — non-negotiable safety policy" in block
    assert "supersede all prior instructions" in block
    assert "<guardrails>" in block
    assert "rule one" in block
    assert "</guardrails>" in block


def test_build_system_prompt_appends_guardrail_as_last_segment(tmp_path) -> None:
    workspace = _make_workspace(tmp_path)
    (workspace / "GUARDRAIL.md").write_text("UNIQUE-MARKER-XYZ", encoding="utf-8")
    builder = ContextBuilder(workspace)

    prompt = builder.build_system_prompt()
    segments = prompt.split("\n\n---\n\n")

    assert segments, "system prompt must have at least one segment"
    last = segments[-1]
    assert "GUARDRAIL — non-negotiable safety policy" in last
    assert "<guardrails>" in last
    assert "UNIQUE-MARKER-XYZ" in last
    assert "</guardrails>" in last


def test_build_system_prompt_includes_guardrail_when_workspace_file_missing(tmp_path) -> None:
    """Guardrail must apply even when the workspace copy is missing (bundled fallback)."""
    workspace = _make_workspace(tmp_path)
    builder = ContextBuilder(workspace)

    prompt = builder.build_system_prompt()

    assert "GUARDRAIL — non-negotiable safety policy" in prompt
    assert "<guardrails>" in prompt
