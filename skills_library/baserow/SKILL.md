---
name: baserow
description: Deterministic Baserow CLI for row CRUD and schema inspection across Trendia, BAH Studios, and Minerva databases.
metadata: {"nanobot":{"requires":{"bins":["python3"]}}}
---

# baserow

## Objectiu
Gestionar Baserow de manera determinista per a un agent: llegir i modificar files, inspeccionar esquemes i planificar canvis sense aplicar mutacions d'estructura.

## Regla principal
No improvisis crides HTTP manuals a Baserow. La ruta real de `workspace` és `/home/larvitar/trendia_stands/.jordana-nanobot/workspace`; no facis servir cap ruta sota `/root`.

Des de l'arrel de `workspace`, usa sempre el Python del virtualenv de l'usuari:

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py <command> ...
```

Totes les respostes del CLI són JSON estable amb:
- `ok`
- `status`
- `account`
- `operation`
- `dry_run`
- `result`
- `error`
- `warnings`

## Autenticació
Files i lectura de metadades via database token:
- `BASEROW_TOKEN_TRENDIA`
- `BASEROW_TOKEN_BAH_STUDIOS`
- `BASEROW_TOKEN_MINERVA`

Config comuna:
- `BASEROW_BASE_URL`, per defecte `https://api.baserow.io`
- `BASEROW_DEFAULT_ACCOUNT`, per defecte `bah_studios`

Els database tokens fan servir `Authorization: Token ...`. Les operacions JWT de canvi d'estructura no existeixen en aquest skill ara mateix i retornen `SCHEMA_OPERATIONS_UNAVAILABLE`.

## Instruccions crítiques per a agents
Per crear, llegir, actualitzar o eliminar files, no facis servir JWT. No demanis JWT a l'usuari. No cridis directament l'API HTTP de Baserow.

Si l'usuari et passa un token nou, no el tractis com a JWT. Els tokens configurats en aquest skill són database tokens i s'han d'usar només a través del CLI, que envia `Authorization: Token ...` automàticament.

Usa sempre el CLI amb l'`account` correcte:

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios create-row --table-id 945959 --payload '{"Name":"Test"}'
```

Si reps `401 ERROR_INVALID_ACCESS_TOKEN`, gairebé segur que estàs fent servir el camí equivocat: JWT, una crida HTTP manual, un endpoint incorrecte o instruccions antigues. No demanis un JWT vigent com a solució. Reintenta l'operació amb el CLI des de l'arrel de `workspace` i amb l'`account` correcte:

```bash
cd /home/larvitar/trendia_stands/.jordana-nanobot/workspace
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios <command> ...
```

Test real validat a BAH Studios:
- `create-row` a `Embut de ventes` (`table_id=945959`) amb `{"Name":"__baserow_skill_write_test__"}` va retornar `status: 200` i va crear la fila `id: 34`.
- `delete-row --confirm` sobre la fila `34` va retornar `status: 204`.
- Després es va verificar `list-rows --table-id 945959 --size 1` amb `count: 0`.

Conclusió: row CRUD funciona amb database token. JWT no és necessari per files i està desactivat per canvis d'estructura.

## Flux recomanat per a agents
Primer inspecciona:

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios inspect-schema --database-id 424353
```

Per actualitzar la còpia local de l'esquema de totes les bases conegudes, usa:

```bash
bin/update-baserow-schemas.sh
```

Aquest script escriu els snapshots a `schemas/baserow/latest.json`, a fitxers per base de dades i a `schemas/baserow/archive/`.

Opcionalment, planifica un manifest JSON en mode dry-run:

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios plan-schema --manifest /path/to/manifest.json
```

No apliquis manifests ni canvis d'estructura fins que s'afegeixi autenticació JWT explícita al skill.

## Manifest JSON
Forma mínima:

```json
{
  "database_id": 424353,
  "tables": [
    {
      "name": "Companies",
      "fields": [
        {"name": "Name", "type": "text"},
        {"name": "Status", "type": "single_select", "select_options": [{"value": "Active", "color": "light-green"}]}
      ]
    }
  ]
}
```

Opcions destructives de planificació:
- `delete_missing_tables: true` al manifest permet planificar eliminació de taules absents del manifest.
- `delete_missing_fields: true` dins una taula permet planificar eliminació de camps absents.
- Les eliminacions i els canvis de `type` només es planifiquen; no s'apliquen ara mateix.

## Files

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios create-row --table-id 945959 --payload '{"Name":"Test"}'
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios delete-row --table-id 945959 --row-id 34 --confirm
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia list-rows --table-id 944551 --size 50
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia get-row --table-id 944551 --row-id 1
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia create-row --table-id 944551 --payload '{"company_name":"Nova Bridge Labs"}'
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia update-row --table-id 944551 --row-id 1 --payload '{"status":"Active"}'
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account trendia delete-row --table-id 944551 --row-id 1 --confirm
```

`delete-row` sense `--confirm` és sempre un dry-run.

## Taules i camps

```bash
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios list-tables
/home/larvitar/nanobot-env/bin/python3 skills/baserow/cli.py --account bah_studios list-fields --table-id 944444
```

`create-table`, `update-table`, `delete-table`, `create-field`, `update-field`, `delete-field` i `apply-schema` no estan disponibles ara mateix.

## Field Values
- Text and number fields: envia valors directes.
- Single select: envia el text de l'opció o l'id de l'opció.
- Multiple select: envia una llista de textos o ids.
- Link to table: envia ids o valors del camp primari; envia sempre la llista completa de relacions desitjades.

## Bases conegudes
- BAH Studios: `database_id=424353`
- Trendia: `database_id=424426`
- Minerva: `database_id=424427`
