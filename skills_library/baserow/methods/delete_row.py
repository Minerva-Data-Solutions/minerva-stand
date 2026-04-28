from __future__ import annotations

from methods.base import BaserowAPI


def run(base_url: str, token: str, table_id: int | str, row_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "DELETE", f"/api/database/rows/table/{table_id}/{row_id}/")
    return result.status, result.body
