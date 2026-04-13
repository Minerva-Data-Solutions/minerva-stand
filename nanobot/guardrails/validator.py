from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Any, Iterable

from nanobot.config.loader import get_config_path
from nanobot.guardrails.patterns import (
    DANGEROUS_COMMAND_NAMES,
    DANGEROUS_SHELL_PATTERNS,
    PROMPT_INJECTION_PATTERNS,
)
from nanobot.guardrails.schema import GuardrailsPolicy, ToolPolicy
from nanobot.guardrails.types import ActionRequest, ValidationResult

_COMMAND_SPLIT_RE = re.compile(r"(?:&&|\|\||;|\|)")
_POSIX_PATH_RE = re.compile(r"(?:^|[\s|>'\"])(/[^\s\"'>;|<]+)")
_HOME_PATH_RE = re.compile(r"(?:^|[\s|>'\"])(~[^\s\"'>;|<]*)")
_WIN_PATH_RE = re.compile(r"[A-Za-z]:\\[^\s\"'|><;]*")
_TEXT_KEYS = {
    "command",
    "content",
    "query",
    "message",
    "prompt",
    "instructions",
    "text",
    "new_text",
    "old_text",
}


def validate_action(action: ActionRequest, policy: GuardrailsPolicy) -> ValidationResult:
    tool_policy = policy.tools.get(action.tool_name, ToolPolicy())
    command_result = _validate_commands(action, tool_policy)
    if not command_result.allowed:
        return command_result
    path_result = _validate_paths(action, tool_policy)
    if not path_result.allowed:
        return path_result
    prompt_result = _validate_prompt_injection(action)
    if not prompt_result.allowed:
        return prompt_result
    return ValidationResult(allowed=True)


def _validate_commands(action: ActionRequest, policy: ToolPolicy) -> ValidationResult:
    if action.tool_name != "exec":
        return ValidationResult(allowed=True)
    command = str(action.params.get("command") or "")
    command_names = _extract_command_names(command)
    blocked = {item.lower() for item in policy.blocked_commands}
    allowed = {item.lower() for item in policy.allowed_commands}
    for name in command_names:
        if name in blocked or name in DANGEROUS_COMMAND_NAMES:
            return ValidationResult(
                allowed=False,
                reason_code="blocked_command",
                message=f"blocked command '{name}'",
                matched_rule=name,
                metadata={"command": command},
            )
    if allowed and any(name not in allowed for name in command_names):
        blocked_name = next(name for name in command_names if name not in allowed)
        return ValidationResult(
            allowed=False,
            reason_code="command_not_allowed",
            message=f"command '{blocked_name}' is not in the allowlist",
            matched_rule=blocked_name,
            metadata={"command": command},
        )
    for pattern in DANGEROUS_SHELL_PATTERNS:
        if pattern.search(command):
            return ValidationResult(
                allowed=False,
                reason_code="unsafe_operation",
                message="unsafe shell pattern detected",
                matched_rule=pattern.pattern,
                metadata={"command": command},
            )
    return ValidationResult(allowed=True)


def _validate_paths(action: ActionRequest, policy: ToolPolicy) -> ValidationResult:
    candidates = _extract_candidate_paths(action)
    if not candidates:
        return ValidationResult(allowed=True)
    allowed_paths = [_expand_policy_path(item, action.workspace) for item in policy.allowed_paths]
    blocked_paths = [_expand_policy_path(item, action.workspace) for item in policy.blocked_paths]
    for path in candidates:
        is_allowed = any(_is_relative_to(path, allowed_path) for allowed_path in allowed_paths)
        if any(_is_relative_to(path, blocked_path) for blocked_path in blocked_paths) and not is_allowed:
            return ValidationResult(
                allowed=False,
                reason_code="blocked_path",
                message=f"path '{path}' is blocked",
                matched_rule=str(path),
                metadata={"path": str(path)},
            )
        if allowed_paths and not is_allowed:
            return ValidationResult(
                allowed=False,
                reason_code="path_not_allowed",
                message=f"path '{path}' is outside allowed paths",
                matched_rule=str(path),
                metadata={"path": str(path)},
            )
    return ValidationResult(allowed=True)


def _validate_prompt_injection(action: ActionRequest) -> ValidationResult:
    for fragment in _extract_text_fragments(action.params):
        for pattern in PROMPT_INJECTION_PATTERNS:
            if pattern.search(fragment):
                return ValidationResult(
                    allowed=False,
                    reason_code="prompt_injection",
                    message="prompt injection pattern detected",
                    matched_rule=pattern.pattern,
                    metadata={"fragment": fragment[:200]},
                )
    return ValidationResult(allowed=True)


def _extract_command_names(command: str) -> list[str]:
    names: list[str] = []
    for segment in _COMMAND_SPLIT_RE.split(command):
        text = segment.strip()
        if not text:
            continue
        try:
            tokens = shlex.split(text, posix=True)
        except ValueError:
            tokens = text.split()
        if not tokens:
            continue
        names.append(Path(tokens[0]).name.lower())
    return names


def _extract_candidate_paths(action: ActionRequest) -> list[Path]:
    candidates: list[Path] = []
    for key, value in action.params.items():
        key_lower = key.lower()
        if isinstance(value, str) and _looks_like_path_key(key_lower):
            path = _resolve_candidate_path(value, action.workspace)
            if path is not None:
                candidates.append(path)
        elif isinstance(value, list) and _looks_like_path_key(key_lower):
            for item in value:
                if isinstance(item, str):
                    path = _resolve_candidate_path(item, action.workspace)
                    if path is not None:
                        candidates.append(path)
    if action.tool_name == "exec":
        command = str(action.params.get("command") or "")
        for raw in _extract_command_paths(command):
            path = _resolve_candidate_path(raw, action.workspace)
            if path is not None:
                candidates.append(path)
    return _dedupe_paths(candidates)


def _extract_text_fragments(params: dict[str, Any]) -> list[str]:
    fragments: list[str] = []
    for key, value in params.items():
        key_lower = key.lower()
        if key_lower not in _TEXT_KEYS:
            continue
        fragments.extend(_flatten_strings(value))
    return [fragment for fragment in fragments if len(fragment) >= 16]


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_flatten_strings(item))
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for item in value.values():
            result.extend(_flatten_strings(item))
        return result
    return []


def _expand_policy_path(raw: str, workspace: Path) -> Path:
    expanded = raw.replace("${WORKSPACE}", str(workspace))
    if "${MEDIA}" in expanded:
        media_dir = (get_config_path().parent / "media").expanduser().resolve(strict=False)
        expanded = expanded.replace("${MEDIA}", str(media_dir))
    expanded = expanded.replace("${HOME}", str(Path.home()))
    return Path(os.path.expandvars(expanded)).expanduser().resolve(strict=False)


def _resolve_candidate_path(raw: str, workspace: Path) -> Path | None:
    if raw.startswith(("http://", "https://")):
        return None
    expanded = Path(os.path.expandvars(raw)).expanduser()
    if not expanded.is_absolute():
        expanded = workspace / expanded
    return expanded.resolve(strict=False)


def _extract_command_paths(command: str) -> Iterable[str]:
    yield from _WIN_PATH_RE.findall(command)
    yield from _POSIX_PATH_RE.findall(command)
    yield from _HOME_PATH_RE.findall(command)


def _looks_like_path_key(key: str) -> bool:
    return "path" in key or key.endswith("dir")


def _is_relative_to(path: Path, candidate_root: Path) -> bool:
    return path == candidate_root or candidate_root in path.parents


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return ordered
