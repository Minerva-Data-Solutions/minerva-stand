from __future__ import annotations

import argparse
import json
from pathlib import Path

from baserow_client import APIResult, BaserowClient
from config import load_config
from schema_manifest import apply_action, inspect_schema, plan_schema


def _parse_json(text: str | None) -> dict:
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")
    return data


def _body(result: APIResult):
    return result.json()


def _envelope(
    *,
    account: str,
    operation: str,
    status: int,
    result=None,
    dry_run: bool = False,
    warnings: list[str] | None = None,
):
    return {
        "account": account,
        "dry_run": dry_run,
        "error": result if status >= 400 else None,
        "ok": status < 400,
        "operation": operation,
        "result": None if status >= 400 else result,
        "status": status,
        "warnings": warnings or [],
    }


def _print(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


def _print_result(account: str, operation: str, result: APIResult) -> None:
    _print(_envelope(account=account, operation=operation, status=result.status, result=_body(result)))


def _dry_run(account: str, operation: str, result: dict, warnings: list[str] | None = None) -> None:
    _print(_envelope(account=account, operation=operation, status=200, result=result, dry_run=True, warnings=warnings))


def _load_manifest(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    return data


def _add_user_field_names(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--field-ids", dest="user_field_names", action="store_false", default=True)


def _add_confirm(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--confirm", action="store_true")


def _parse_filters(args: argparse.Namespace) -> dict | None:
    return None if not getattr(args, "filters_json", None) else _parse_json(args.filters_json)


def _ensure_confirmed(args: argparse.Namespace, account: str, operation: str, planned: dict, warning: str) -> bool:
    if args.confirm:
        return True
    _dry_run(account, operation, planned, [warning])
    return False


def _run_apply_schema(client: BaserowClient, account: str, manifest: dict, confirm: bool) -> int:
    database_id = manifest.get("database_id")
    if database_id is None:
        raise ValueError("Manifest must include database_id")
    status, live = inspect_schema(client, account, database_id)
    if status >= 400:
        _print(_envelope(account=account, operation="apply-schema", status=status, result=live))
        return 1
    plan = plan_schema(live, manifest | {"account": account})
    if not confirm:
        _dry_run(account, "apply-schema", plan, ["Pass --confirm to apply this plan."])
        return 0

    applied = []
    final_status = 200
    for action in plan["actions"]:
        if action.get("requires_confirm") and not confirm:
            final_status = 400
            applied.append({"action": action, "status": 400, "body": {"error": "CONFIRM_REQUIRED"}})
            break
        action_status, body = apply_action(client, action)
        applied.append({"action": action, "status": action_status, "body": body})
        if action_status >= 400:
            final_status = action_status
            break
    _print(_envelope(account=account, operation="apply-schema", status=final_status, result={"plan": plan, "applied": applied}))
    return 0 if final_status < 400 else 1


def _build_parser(default_account: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic Baserow CLI")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--account", default=default_account)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-databases")

    p = sub.add_parser("list-tables")
    p.add_argument("--database-id")

    p = sub.add_parser("list-fields")
    p.add_argument("--table-id", required=True)

    p = sub.add_parser("list-rows")
    p.add_argument("--table-id", required=True)
    p.add_argument("--page", type=int)
    p.add_argument("--size", type=int)
    p.add_argument("--search")
    p.add_argument("--order-by")
    p.add_argument("--filters-json")
    _add_user_field_names(p)

    p = sub.add_parser("get-row")
    p.add_argument("--table-id", required=True)
    p.add_argument("--row-id", required=True)
    _add_user_field_names(p)

    p = sub.add_parser("create-row")
    p.add_argument("--table-id", required=True)
    p.add_argument("--payload", required=True)
    _add_user_field_names(p)

    p = sub.add_parser("update-row")
    p.add_argument("--table-id", required=True)
    p.add_argument("--row-id", required=True)
    p.add_argument("--payload", required=True)
    _add_user_field_names(p)

    p = sub.add_parser("delete-row")
    p.add_argument("--table-id", required=True)
    p.add_argument("--row-id", required=True)
    _add_confirm(p)

    p = sub.add_parser("create-table")
    p.add_argument("--database-id", required=True)
    p.add_argument("--name")
    p.add_argument("--payload")

    p = sub.add_parser("update-table")
    p.add_argument("--table-id", required=True)
    p.add_argument("--name")
    p.add_argument("--payload")

    p = sub.add_parser("delete-table")
    p.add_argument("--table-id", required=True)
    _add_confirm(p)

    p = sub.add_parser("create-field")
    p.add_argument("--table-id", required=True)
    p.add_argument("--payload", required=True)

    p = sub.add_parser("update-field")
    p.add_argument("--field-id", required=True)
    p.add_argument("--payload", required=True)
    _add_confirm(p)

    p = sub.add_parser("delete-field")
    p.add_argument("--field-id", required=True)
    _add_confirm(p)

    p = sub.add_parser("inspect-schema")
    p.add_argument("--database-id", required=True)

    p = sub.add_parser("plan-schema")
    p.add_argument("--manifest", required=True)
    p.add_argument("--database-id")

    p = sub.add_parser("apply-schema")
    p.add_argument("--manifest", required=True)
    _add_confirm(p)

    return parser


def main() -> int:
    config = load_config()
    parser = _build_parser(config.default_account)
    args = parser.parse_args()
    if args.base_url:
        config = config.__class__(
            base_url=args.base_url,
            accounts=config.accounts,
            default_account=config.default_account,
            first_database_name=config.first_database_name,
            jwt_access_token=config.jwt_access_token,
            jwt_refresh_token=config.jwt_refresh_token,
        )
    client = BaserowClient(config)
    account = args.account

    try:
        if args.command == "list-databases":
            result = client.list_databases()
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "list-tables":
            result = client.list_database_tables_with_token(account, args.database_id) if args.database_id else client.list_all_tables(account)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "list-fields":
            result = client.list_table_fields(account, args.table_id)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "list-rows":
            result = client.list_rows(
                account,
                args.table_id,
                user_field_names=args.user_field_names,
                page=args.page,
                size=args.size,
                search=args.search,
                order_by=args.order_by,
                filters=_parse_filters(args),
            )
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "get-row":
            result = client.get_row(account, args.table_id, args.row_id, user_field_names=args.user_field_names)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "create-row":
            result = client.create_row(account, args.table_id, _parse_json(args.payload), user_field_names=args.user_field_names)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "update-row":
            result = client.update_row(account, args.table_id, args.row_id, _parse_json(args.payload), user_field_names=args.user_field_names)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "delete-row":
            planned = {"action": "delete_row", "row_id": args.row_id, "table_id": args.table_id}
            if not _ensure_confirmed(args, account, args.command, planned, "Pass --confirm to delete this row."):
                return 0
            result = client.delete_row(account, args.table_id, args.row_id)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "create-table":
            payload = _parse_json(args.payload) if args.payload else {"name": args.name}
            result = client.create_table(args.database_id, payload)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "update-table":
            payload = _parse_json(args.payload) if args.payload else {"name": args.name}
            result = client.update_table(args.table_id, payload)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "delete-table":
            planned = {"action": "delete_table", "table_id": args.table_id}
            if not _ensure_confirmed(args, account, args.command, planned, "Pass --confirm to delete this table."):
                return 0
            result = client.delete_table(args.table_id)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "create-field":
            result = client.create_field(args.table_id, _parse_json(args.payload))
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "update-field":
            payload = _parse_json(args.payload)
            planned = {"action": "update_field", "field_id": args.field_id, "payload": payload}
            if "type" in payload and not _ensure_confirmed(args, account, args.command, planned, "Pass --confirm to update a field type."):
                return 0
            result = client.update_field(args.field_id, payload)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "delete-field":
            planned = {"action": "delete_field", "field_id": args.field_id}
            if not _ensure_confirmed(args, account, args.command, planned, "Pass --confirm to delete this field."):
                return 0
            result = client.delete_field(args.field_id)
            _print_result(account, args.command, result)
            return 0 if result.status < 400 else 1
        if args.command == "inspect-schema":
            status, schema = inspect_schema(client, account, args.database_id)
            _print(_envelope(account=account, operation=args.command, status=status, result=schema))
            return 0 if status < 400 else 1
        if args.command == "plan-schema":
            manifest = _load_manifest(args.manifest)
            database_id = args.database_id or manifest.get("database_id")
            if database_id is None:
                raise ValueError("Provide --database-id or include database_id in the manifest")
            status, live = inspect_schema(client, account, database_id)
            if status >= 400:
                _print(_envelope(account=account, operation=args.command, status=status, result=live))
                return 1
            plan = plan_schema(live, manifest | {"account": account, "database_id": database_id})
            _print(_envelope(account=account, operation=args.command, status=200, result=plan, dry_run=True))
            return 0
        if args.command == "apply-schema":
            return _run_apply_schema(client, account, _load_manifest(args.manifest), args.confirm)
        raise RuntimeError(f"Unknown command: {args.command}")
    except Exception as exc:
        _print(_envelope(account=account, operation=args.command, status=1, result={"error": exc.__class__.__name__, "description": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
