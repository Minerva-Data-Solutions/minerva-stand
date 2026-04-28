from __future__ import annotations

from dataclasses import dataclass


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


TABLES = [
    TableSchema(id=944548, name="Embut de ventes", database_id=424426),
    TableSchema(id=944551, name="Clients", database_id=424426),
    TableSchema(id=944555, name="Activitat", database_id=424426),
    TableSchema(id=944558, name="Tasques", database_id=424426),
    TableSchema(id=944559, name="Ofertes", database_id=424426),
]

FIELDS = [
    FieldSchema(id=8214118, name="status", type="single_select", table_id=944548,
                select_options=["objectius", "standby", "contactat", "interessant", "demo", "freemium", "valoració demo", "negociació"]),
    FieldSchema(id=8214119, name="notes", type="text", table_id=944548),

    FieldSchema(id=8214164, name="company_name", type="text", table_id=944551),
    FieldSchema(id=8214165, name="first_name", type="text", table_id=944551),
    FieldSchema(id=8214166, name="last_name", type="text", table_id=944551),
    FieldSchema(id=8214167, name="full_name", type="text", table_id=944551),
    FieldSchema(id=8214168, name="title", type="text", table_id=944551),
    FieldSchema(id=8214169, name="email", type="text", table_id=944551),
    FieldSchema(id=8214170, name="linkedin_url", type="text", table_id=944551),
    FieldSchema(id=8214171, name="phone", type="text", table_id=944551),
    FieldSchema(id=8214172, name="notes", type="text", table_id=944551),
    FieldSchema(id=8214173, name="type", type="single_select", table_id=944551,
                select_options=["company", "contact"]),
    FieldSchema(id=8214174, name="funnel_status", type="single_select", table_id=944551,
                select_options=["objectius", "standby", "contactat", "interessant", "demo", "freemium", "valoració demo", "negociació"]),

    FieldSchema(id=8214175, name="event_type", type="text", table_id=944555),
    FieldSchema(id=8214176, name="date", type="text", table_id=944555),
    FieldSchema(id=8214177, name="lead_name", type="text", table_id=944555),
    FieldSchema(id=8214178, name="notes", type="text", table_id=944555),

    FieldSchema(id=8214179, name="title", type="text", table_id=944558),
    FieldSchema(id=8214180, name="related_lead", type="text", table_id=944558),
    FieldSchema(id=8214181, name="due_date", type="text", table_id=944558),

    FieldSchema(id=8214182, name="name", type="text", table_id=944559),
    FieldSchema(id=8214183, name="price_from", type="text", table_id=944559),
    FieldSchema(id=8214184, name="notes", type="text", table_id=944559),
]

CONTACTS_SELECT_VALUES = {
    "funnel_status": ["objectius", "standby", "contactat", "interessant", "demo", "freemium", "valoració demo", "negociació"],
    "type": ["company", "contact"],
}
