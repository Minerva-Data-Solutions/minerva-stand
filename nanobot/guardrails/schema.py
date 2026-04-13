from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class _BaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ToolPolicy(_BaseModel):
    allowed_commands: list[str] = Field(default_factory=list)
    blocked_commands: list[str] = Field(default_factory=list)
    allowed_paths: list[str] = Field(default_factory=list)
    blocked_paths: list[str] = Field(default_factory=list)


class GuardrailsPolicy(_BaseModel):
    tools: dict[str, ToolPolicy] = Field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "GuardrailsPolicy":
        return cls.model_validate(data)
