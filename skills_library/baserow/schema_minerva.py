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
    TableSchema(id=944562, name="Embut de ventes", database_id=424427),
    TableSchema(id=944563, name="Clients", database_id=424427),
    TableSchema(id=944567, name="Activitat", database_id=424427),
    TableSchema(id=944570, name="Tasques", database_id=424427),
    TableSchema(id=944571, name="Ofertes", database_id=424427),
]

FIELDS = [
    FieldSchema(id=8214221, name="status", type="single_select", table_id=944562,
                select_options=["objectius", "standby", "contactat", "interessant", "reunió de 15'", "preparació proposta", "presentació de pressupost i proposta", "negociació"]),
    FieldSchema(id=8214222, name="notes", type="text", table_id=944562),

    FieldSchema(id=8214229, name="company_name", type="text", table_id=944563),
    FieldSchema(id=8214230, name="first_name", type="text", table_id=944563),
    FieldSchema(id=8214231, name="last_name", type="text", table_id=944563),
    FieldSchema(id=8214232, name="full_name", type="text", table_id=944563),
    FieldSchema(id=8214233, name="title", type="text", table_id=944563),
    FieldSchema(id=8214234, name="email", type="text", table_id=944563),
    FieldSchema(id=8214235, name="linkedin_url", type="text", table_id=944563),
    FieldSchema(id=8214236, name="phone", type="text", table_id=944563),
    FieldSchema(id=8214237, name="notes", type="text", table_id=944563),
    FieldSchema(id=8214238, name="type", type="single_select", table_id=944563,
                select_options=["company", "contact"]),
    FieldSchema(id=8214239, name="funnel_status", type="single_select", table_id=944563,
                select_options=["objectius", "standby", "contactat", "interessant", "reunió de 15'", "preparació proposta", "presentació de pressupost i proposta", "negociació"]),

    FieldSchema(id=8214240, name="event_type", type="text", table_id=944567),
    FieldSchema(id=8214241, name="date", type="text", table_id=944567),
    FieldSchema(id=8214242, name="lead_name", type="text", table_id=944567),
    FieldSchema(id=8214243, name="notes", type="text", table_id=944567),

    FieldSchema(id=8214244, name="title", type="text", table_id=944570),
    FieldSchema(id=8214245, name="related_lead", type="text", table_id=944570),
    FieldSchema(id=8214246, name="due_date", type="text", table_id=944570),

    FieldSchema(id=8214247, name="name", type="text", table_id=944571),
    FieldSchema(id=8214248, name="price_from", type="text", table_id=944571),
    FieldSchema(id=8214249, name="notes", type="text", table_id=944571),
]

CONTACTS_SELECT_VALUES = {
    "funnel_status": ["objectius", "standby", "contactat", "interessant", "reunió de 15'", "preparació proposta", "presentació de pressupost i proposta", "negociació"],
    "type": ["company", "contact"],
}
