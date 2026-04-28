from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TableSchema:
    id: int | str | None
    name: str
    database_id: int | str | None


@dataclass(frozen=True)
class FieldSchema:
    id: int | str | None
    name: str
    type: str | None = None
    table_id: int | str | None = None
    select_options: list[str] | None = None
    required: bool | None = None
    primary: bool | None = None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class SchemaSnapshot:
    account: str
    database_id: int | str | None
    tables: list[TableSchema] = field(default_factory=list)
    fields: list[FieldSchema] = field(default_factory=list)


TABLES: list[TableSchema] = []
FIELDS: list[FieldSchema] = []
