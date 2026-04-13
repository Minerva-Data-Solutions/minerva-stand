from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.config.schema import GuardrailsConfig
from nanobot.guardrails.default_policy import build_default_policy
from nanobot.guardrails.schema import GuardrailsPolicy


class GuardrailsLoader:
    def __init__(self, config: GuardrailsConfig) -> None:
        self.config = config
        self.enabled = config.enabled
        self.policy_path = Path(config.policy_path).expanduser()
        self._cached_policy: GuardrailsPolicy | None = None
        self._cached_signature: tuple[bool, int] | None = None
        self._missing_logged = False

    def get_policy(self) -> GuardrailsPolicy:
        if not self.enabled:
            return GuardrailsPolicy()
        signature = self._signature()
        if (
            self._cached_policy is not None
            and self._cached_signature == signature
            and not self.config.reload_on_change
        ):
            return self._cached_policy
        if self._cached_policy is not None and self._cached_signature == signature:
            return self._cached_policy
        policy = self._load_policy()
        self._cached_policy = policy
        self._cached_signature = signature
        return policy

    def _load_policy(self) -> GuardrailsPolicy:
        merged = build_default_policy()
        if not self.policy_path.exists():
            if not self._missing_logged:
                logger.warning(
                    "Guardrails policy file not found at {}; using built-in defaults",
                    self.policy_path,
                )
                self._missing_logged = True
            return GuardrailsPolicy.from_mapping(merged)
        try:
            raw = json.loads(self.policy_path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Failed to load guardrails policy from {}", self.policy_path)
            return GuardrailsPolicy.from_mapping(merged)
        data = _deep_merge(merged, raw if isinstance(raw, dict) else {})
        try:
            return GuardrailsPolicy.from_mapping(data)
        except Exception:
            logger.exception("Guardrails policy at {} is invalid", self.policy_path)
            return GuardrailsPolicy.from_mapping(merged)

    def _signature(self) -> tuple[bool, int]:
        if not self.policy_path.exists():
            return False, -1
        try:
            return True, self.policy_path.stat().st_mtime_ns
        except OSError:
            return True, -1


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
