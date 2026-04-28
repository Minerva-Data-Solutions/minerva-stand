from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from baserow_client import BaserowClient
from config import load_config
from schema_manifest import inspect_schema


DEFAULT_DATABASES = {
    "bah_studios": "424353",
    "trendia": "424426",
    "minerva": "424427",
}


def _parse_database(value: str) -> tuple[str, str]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("Expected account:database_id")
    account, database_id = value.split(":", 1)
    account = account.strip()
    database_id = database_id.strip()
    if not account or not database_id:
        raise argparse.ArgumentTypeError("Expected account:database_id")
    return account, database_id


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export current Baserow schemas")
    parser.add_argument(
        "--database",
        action="append",
        type=_parse_database,
        help="Database to inspect as account:database_id. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[2] / "schemas" / "baserow"),
        help="Directory where schema snapshots are written.",
    )
    args = parser.parse_args()

    databases = args.database or list(DEFAULT_DATABASES.items())
    output_dir = Path(args.output_dir).resolve()
    generated_at = datetime.now(timezone.utc).isoformat()
    client = BaserowClient(load_config())

    snapshots = []
    failures = []

    for account, database_id in databases:
        status, schema = inspect_schema(client, account, database_id)
        entry = {
            "account": account,
            "database_id": database_id,
            "generated_at": generated_at,
            "ok": status < 400,
            "schema": schema if status < 400 else None,
            "status": status,
            "error": schema if status >= 400 else None,
        }
        safe_name = f"{account}_{database_id}"
        _write_json(output_dir / f"{safe_name}.schema.json", entry)
        snapshots.append(entry)
        if status >= 400:
            failures.append({"account": account, "database_id": database_id, "status": status, "error": schema})

    payload = {
        "databases": snapshots,
        "generated_at": generated_at,
        "ok": not failures,
    }
    timestamp = generated_at.replace(":", "").replace("+", "Z")
    _write_json(output_dir / "latest.json", payload)
    _write_json(output_dir / "archive" / f"{timestamp}.json", payload)

    print(json.dumps({"ok": not failures, "output_dir": str(output_dir), "failures": failures}, ensure_ascii=False, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
