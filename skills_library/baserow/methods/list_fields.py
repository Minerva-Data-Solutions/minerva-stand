from __future__ import annotations

from methods.base import BaserowAPI


def run(base_url: str, token: str, table_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "GET", f"/api/database/fields/table/{table_id}/")
    return result.status, result.body
