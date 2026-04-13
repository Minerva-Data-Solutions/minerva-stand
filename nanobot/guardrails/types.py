from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ActionRequest:
    tool_name: str
    params: dict[str, Any]
    workspace: Path


@dataclass(slots=True)
class ValidationResult:
    allowed: bool
    reason_code: str | None = None
    message: str | None = None
    matched_rule: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
