from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from baserow_client import BaserowClient
from config import load_config


def _pretty(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)


def _parse_json(text: str) -> Any:
    return json.loads(text)


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_")


def main() -> None:
    config = load_config()
    client = BaserowClient(config)
    account_name = config.default_account
    status, body = client.list_all_tables(account_name=account_name)
    tables = _parse_json(body) if status == 200 else []

    enriched_tables = []
    for table in tables:
        table_id = table.get("id")
        field_result = client.list_table_fields(account_name=account_name, table_id=table_id)
        field_status, field_body = field_result.status, field_result.body
        fields = _parse_json(field_body) if field_status == 200 else []
        enriched_tables.append({
            "table": table,
            "fields_status": field_status,
            "fields": fields,
        })

    output = {
        "account": account_name,
        "status": status,
        "tables": tables,
        "enriched_tables": enriched_tables,
    }
    print(_pretty(output))

    schema_path = Path(__file__).resolve().parent / f"schema_{_slug(account_name)}.py"
    schema_lines = [
        'from __future__ import annotations',
        '',
        'from dataclasses import dataclass',
        '',
        '@dataclass(frozen=True)',
        'class TableSchema:',
        '    id: int | str | None',
        '    name: str',
        '    database_id: int | str | None',
        '',
        '@dataclass(frozen=True)',
        'class FieldSchema:',
        '    id: int | str | None',
        '    name: str',
        '    type: str | None = None',
        '    table_id: int | str | None = None',
        '',
        'TABLES = [',
    ]
    for table in tables:
        schema_lines.append(
            f"    TableSchema(id={table.get('id')!r}, name={table.get('name')!r}, database_id={table.get('database_id')!r}),"
        )
    schema_lines.extend([']', '', 'FIELDS = ['])
    for item in enriched_tables:
        table = item["table"]
        for field in item["fields"]:
            schema_lines.append(
                f"    FieldSchema(id={field.get('id')!r}, name={field.get('name')!r}, type={field.get('type')!r}, table_id={table.get('id')!r}),"
            )
    schema_lines.extend([']', ''])
    schema_path.write_text('\n'.join(schema_lines), encoding='utf-8')


if __name__ == "__main__":
    main()
