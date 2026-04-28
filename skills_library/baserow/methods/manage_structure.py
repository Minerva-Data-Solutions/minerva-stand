from __future__ import annotations

from methods.base import BaserowAPI


def create_table(base_url: str, token: str, database_id: int | str, name: str, data: list | None = None, first_row_header: bool = False) -> tuple[int, str]:
    payload = {
        "name": name,
        "data": data if data is not None else [],
        "first_row_header": first_row_header,
    }
    result = BaserowAPI(base_url).request(token, "POST", f"/api/database/tables/database/{database_id}/", payload=payload, auth_scheme="JWT")
    return result.status, result.body


def create_async_table(base_url: str, token: str, database_id: int | str, name: str, data: list | None = None, first_row_header: bool = False) -> tuple[int, str]:
    payload = {
        "name": name,
        "data": data if data is not None else [],
        "first_row_header": first_row_header,
    }
    result = BaserowAPI(base_url).request(token, "POST", f"/api/database/tables/database/{database_id}/async/", payload=payload, auth_scheme="JWT")
    return result.status, result.body


def list_tables(base_url: str, token: str, database_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "GET", f"/api/database/tables/database/{database_id}/", auth_scheme="JWT")
    return result.status, result.body


def update_table(base_url: str, token: str, table_id: int | str, name: str) -> tuple[int, str]:
    payload = {"name": name}
    result = BaserowAPI(base_url).request(token, "PATCH", f"/api/database/tables/{table_id}/", payload=payload, auth_scheme="JWT")
    return result.status, result.body


def delete_table(base_url: str, token: str, table_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "DELETE", f"/api/database/tables/{table_id}/", auth_scheme="JWT")
    return result.status, result.body


def create_field(base_url: str, token: str, table_id: int | str, name: str, field_type: str, **kwargs) -> tuple[int, str]:
    payload = {"name": name, "type": field_type, **kwargs}
    result = BaserowAPI(base_url).request(token, "POST", f"/api/database/fields/table/{table_id}/", payload=payload, auth_scheme="JWT")
    return result.status, result.body


def update_field(base_url: str, token: str, field_id: int | str, **kwargs) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "PATCH", f"/api/database/fields/{field_id}/", payload=kwargs, auth_scheme="JWT")
    return result.status, result.body


def delete_field(base_url: str, token: str, field_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "DELETE", f"/api/database/fields/{field_id}/", auth_scheme="JWT")
    return result.status, result.body


def list_fields(base_url: str, token: str, table_id: int | str) -> tuple[int, str]:
    result = BaserowAPI(base_url).request(token, "GET", f"/api/database/fields/table/{table_id}/", auth_scheme="JWT")
    return result.status, result.body
