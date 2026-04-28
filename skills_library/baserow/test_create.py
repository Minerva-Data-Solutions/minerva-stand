from __future__ import annotations

import json

from baserow_client import BaserowClient
from config import load_config

account = "bah_studios"
table_id = 945959

payload = {
    "Name": "Nova Bridge Labs",
    "Stage": "Prospect",
}

result = BaserowClient(load_config()).create_row(account, table_id, payload)
print(json.dumps({"status": result.status, "body": result.json()}, indent=2, ensure_ascii=False, sort_keys=True))