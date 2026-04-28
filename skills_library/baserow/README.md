# Baserow Skill

Deterministic Baserow CLI/API wrapper for agents.

## Auth Model
- Row CRUD and table/field reads use database tokens: `Authorization: Token ...`.
- JWT-backed table, field, and type mutations are intentionally unavailable for now.
- Tokens load from environment or `skills/baserow/.env`.

Required row tokens:
- `BASEROW_TOKEN_TRENDIA`
- `BASEROW_TOKEN_BAH_STUDIOS`
- `BASEROW_TOKEN_MINERVA`

Optional:
- `BASEROW_BASE_URL`
- `BASEROW_DEFAULT_ACCOUNT`

## Deterministic Output
Every command prints one sorted JSON envelope:

```json
{
  "account": "bah_studios",
  "dry_run": false,
  "error": null,
  "ok": true,
  "operation": "list-tables",
  "result": [],
  "status": 200,
  "warnings": []
}
```

## Agent Workflow

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios inspect-schema --database-id 424353
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios plan-schema --manifest /path/to/manifest.json
```

`inspect-schema` and `plan-schema` are available. `apply-schema` and direct schema mutation commands return `SCHEMA_OPERATIONS_UNAVAILABLE`.

Refresh the local schema copy for all known databases:

```bash
bin/update-baserow-schemas.sh
```

The script writes `schemas/baserow/latest.json`, one `*.schema.json` file per database, and archived timestamped snapshots.

## Row Commands

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia list-rows --table-id 944551 --size 50
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia get-row --table-id 944551 --row-id 1
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia create-row --table-id 944551 --payload '{"company_name":"Nova Bridge Labs"}'
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia update-row --table-id 944551 --row-id 1 --payload '{"status":"Active"}'
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia delete-row --table-id 944551 --row-id 1 --confirm
```

`delete-row` requires `--confirm`.

## Schema Commands

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios list-tables
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios list-fields --table-id 944444
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios inspect-schema --database-id 424353
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios plan-schema --manifest /path/to/manifest.json
```

Direct table/field create, update, delete, and `apply-schema` are not available until JWT support is intentionally enabled.

## Manifest Format

```json
{
  "database_id": 424353,
  "tables": [
    {
      "name": "Companies",
      "delete_missing_fields": false,
      "fields": [
        {"name": "Name", "type": "text"},
        {"name": "Status", "type": "single_select", "select_options": [{"value": "Active", "color": "light-green"}]}
      ]
    }
  ],
  "delete_missing_tables": false
}
```

## Known Databases
- BAH Studios: `424353`
- Trendia: `424426`
- Minerva: `424427`
