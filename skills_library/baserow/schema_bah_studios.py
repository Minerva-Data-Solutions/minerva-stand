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
    TableSchema(id=944444, name="Embut de ventes", database_id=424353),
    TableSchema(id=944445, name="Clients", database_id=424353),
    TableSchema(id=944450, name="Activitat", database_id=424353),
    TableSchema(id=944454, name="Tasques", database_id=424353),
    TableSchema(id=944455, name="Ofertes", database_id=424353),
]

FIELDS = [
    FieldSchema(id=8213220, name="status", type="single_select", table_id=944444,
                select_options=["objectius", "standby", "contactat", "interessant", "presentació i briefing", "preparació proposta", "proposta presentació", "presentació pressupost", "negociació"]),
    FieldSchema(id=8213221, name="notes", type="text", table_id=944444),

    FieldSchema(id=8213140, name="company_name", type="text", table_id=944445),
    FieldSchema(id=8213141, name="first_name", type="text", table_id=944445),
    FieldSchema(id=8213142, name="last_name", type="text", table_id=944445),
    FieldSchema(id=8213143, name="full_name", type="text", table_id=944445),
    FieldSchema(id=8213144, name="title", type="text", table_id=944445),
    FieldSchema(id=8213145, name="email", type="text", table_id=944445),
    FieldSchema(id=8213146, name="linkedin_url", type="text", table_id=944445),
    FieldSchema(id=8213147, name="phone", type="text", table_id=944445),
    FieldSchema(id=8213148, name="notes", type="text", table_id=944445),
    FieldSchema(id=8213149, name="type", type="single_select", table_id=944445,
                select_options=["company", "contact"]),
    FieldSchema(id=8213150, name="funnel_status", type="single_select", table_id=944445,
                select_options=["objectius", "standby", "contactat", "interessant", "presentació i briefing", "preparació proposta", "proposta presentació", "presentació pressupost", "negociació"]),

    FieldSchema(id=8213230, name="event_type", type="text", table_id=944450),
    FieldSchema(id=8213231, name="date", type="text", table_id=944450),
    FieldSchema(id=8213232, name="lead_name", type="text", table_id=944450),
    FieldSchema(id=8213233, name="notes", type="text", table_id=944450),

    FieldSchema(id=8213240, name="title", type="text", table_id=944454),
    FieldSchema(id=8213241, name="related_lead", type="text", table_id=944454),
    FieldSchema(id=8213242, name="due_date", type="text", table_id=944454),

    FieldSchema(id=8213250, name="name", type="text", table_id=944455),
    FieldSchema(id=8213251, name="price_from", type="text", table_id=944455),
    FieldSchema(id=8213252, name="notes", type="text", table_id=944455),
]

CONTACTS_SELECT_VALUES = {
    "funnel_status": ["objectius", "standby", "contactat", "interessant", "presentació i briefing", "preparació proposta", "proposta presentació", "presentació pressupost", "negociació"],
    "type": ["company", "contact"],
}
