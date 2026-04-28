from __future__ import annotations

from typing import Any

from baserow_client import BaserowClient


FIELD_COMPARE_KEYS = (
    "name",
    "type",
    "select_options",
    "number_decimal_places",
    "number_negative",
    "date_format",
    "date_include_time",
    "date_time_format",
    "link_row_table_id",
    "formula",
)


def normalize_field(field: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "id": field.get("id"),
        "name": field.get("name"),
        "type": field.get("type"),
        "primary": bool(field.get("primary", False)),
    }
    if "select_options" in field:
        normalized["select_options"] = sorted(
            [
                {key: option.get(key) for key in ("id", "value", "color") if key in option}
                for option in field.get("select_options", [])
            ],
            key=lambda option: (str(option.get("value", "")), str(option.get("id", ""))),
        )
    for key in FIELD_COMPARE_KEYS:
        if key in field and key not in normalized:
            normalized[key] = field[key]
    return {key: normalized[key] for key in sorted(normalized)}


def normalize_table(table: dict[str, Any], fields: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    normalized: dict[str, Any] = {
        "database_id": table.get("database_id"),
        "id": table.get("id"),
        "name": table.get("name"),
    }
    if fields is not None:
        normalized["fields"] = sorted([normalize_field(field) for field in fields], key=lambda field: str(field.get("name", "")))
    return {key: normalized[key] for key in sorted(normalized)}


def inspect_schema(client: BaserowClient, account: str, database_id: int | str) -> tuple[int, dict[str, Any]]:
    tables_result = client.list_all_tables(account)
    if tables_result.status >= 400:
        return tables_result.status, {"error": tables_result.json()}
    tables = [
        table for table in tables_result.json()
        if str(table.get("database_id")) == str(database_id)
    ]
    normalized_tables = []
    for table in sorted(tables, key=lambda item: str(item.get("name", ""))):
        fields_result = client.list_table_fields(account, table["id"])
        if fields_result.status >= 400:
            return fields_result.status, {"error": fields_result.json(), "table_id": table["id"]}
        normalized_tables.append(normalize_table(table, fields_result.json()))
    return 200, {
        "account": account,
        "database_id": database_id,
        "tables": normalized_tables,
    }


def _field_payload(field: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in field.items() if key not in {"id", "primary", "fields"} and value is not None}
    return {key: payload[key] for key in sorted(payload)}


def _table_payload(table: dict[str, Any]) -> dict[str, Any]:
    payload = {key: value for key, value in table.items() if key not in {"id", "database_id", "fields", "delete_missing_fields"} and value is not None}
    return {key: payload[key] for key in sorted(payload)}


def _find_by_id_or_name(items: list[dict[str, Any]], wanted: dict[str, Any]) -> dict[str, Any] | None:
    wanted_id = wanted.get("id")
    if wanted_id is not None:
        for item in items:
            if str(item.get("id")) == str(wanted_id):
                return item
    wanted_name = wanted.get("name")
    if wanted_name is not None:
        for item in items:
            if item.get("name") == wanted_name:
                return item
    return None


def plan_schema(live_schema: dict[str, Any], desired_schema: dict[str, Any]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    live_tables = live_schema.get("tables", [])
    desired_tables = desired_schema.get("tables", [])
    delete_missing_tables = bool(desired_schema.get("delete_missing_tables", False))

    for desired_table in desired_tables:
        live_table = _find_by_id_or_name(live_tables, desired_table)
        desired_fields = desired_table.get("fields", [])
        if live_table is None:
            actions.append({
                "action": "create_table",
                "database_id": desired_schema.get("database_id") or live_schema.get("database_id"),
                "payload": _table_payload(desired_table),
                "fields": [_field_payload(field) for field in desired_fields],
                "requires_confirm": False,
            })
            continue

        if desired_table.get("id") is not None and desired_table.get("name") and desired_table.get("name") != live_table.get("name"):
            actions.append({
                "action": "update_table",
                "table_id": live_table["id"],
                "payload": {"name": desired_table["name"]},
                "requires_confirm": False,
            })

        live_fields = live_table.get("fields", [])
        for desired_field in desired_fields:
            live_field = _find_by_id_or_name(live_fields, desired_field)
            desired_payload = _field_payload(desired_field)
            if live_field is None:
                actions.append({
                    "action": "create_field",
                    "table_id": live_table["id"],
                    "payload": desired_payload,
                    "requires_confirm": False,
                })
                continue
            update_payload = {}
            for key in FIELD_COMPARE_KEYS:
                if key in desired_payload and desired_payload.get(key) != live_field.get(key):
                    update_payload[key] = desired_payload[key]
            if update_payload:
                actions.append({
                    "action": "update_field",
                    "field_id": live_field["id"],
                    "payload": {key: update_payload[key] for key in sorted(update_payload)},
                    "requires_confirm": "type" in update_payload,
                })

        if desired_table.get("delete_missing_fields"):
            desired_matches = {_find_by_id_or_name(live_fields, field).get("id") for field in desired_fields if _find_by_id_or_name(live_fields, field)}
            for live_field in live_fields:
                if live_field.get("primary") or live_field.get("id") in desired_matches:
                    continue
                actions.append({
                    "action": "delete_field",
                    "field_id": live_field["id"],
                    "requires_confirm": True,
                })

    if delete_missing_tables:
        desired_matches = {_find_by_id_or_name(live_tables, table).get("id") for table in desired_tables if _find_by_id_or_name(live_tables, table)}
        for live_table in live_tables:
            if live_table.get("id") not in desired_matches:
                actions.append({
                    "action": "delete_table",
                    "table_id": live_table["id"],
                    "requires_confirm": True,
                })

    return {
        "account": desired_schema.get("account") or live_schema.get("account"),
        "database_id": desired_schema.get("database_id") or live_schema.get("database_id"),
        "actions": actions,
        "action_count": len(actions),
        "requires_confirm": any(action.get("requires_confirm") for action in actions),
    }


def apply_action(client: BaserowClient, action: dict[str, Any]) -> tuple[int, Any]:
    name = action["action"]
    if name == "create_table":
        result = client.create_table(action["database_id"], action["payload"])
        if result.status >= 400:
            return result.status, result.json()
        table = result.json()
        created_fields = []
        for field_payload in action.get("fields", []):
            field_result = client.create_field(table["id"], field_payload)
            created_fields.append({"status": field_result.status, "body": field_result.json()})
        return result.status, {"table": table, "fields": created_fields}
    if name == "update_table":
        result = client.update_table(action["table_id"], action["payload"])
    elif name == "delete_table":
        result = client.delete_table(action["table_id"])
    elif name == "create_field":
        result = client.create_field(action["table_id"], action["payload"])
    elif name == "update_field":
        result = client.update_field(action["field_id"], action["payload"])
    elif name == "delete_field":
        result = client.delete_field(action["field_id"])
    else:
        return 400, {"error": "UNKNOWN_ACTION", "description": f"Unknown schema action: {name}"}
    if result.body:
        return result.status, result.json()
    return result.status, None
