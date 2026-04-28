from __future__ import annotations

from methods.base import BaserowAPI


def run(base_url: str, token: str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "GET", "/api/database/tables/all-tables/")
    return result.status, result.body
