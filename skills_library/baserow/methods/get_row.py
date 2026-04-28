from __future__ import annotations

from methods.base import BaserowAPI


def run(base_url: str, token: str, table_id: int | str, row_id: int | str, user_field_names: bool = True) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "GET", f"/api/database/rows/table/{table_id}/{row_id}/", query={"user_field_names": str(user_field_names).lower()})
    return result.status, result.body
