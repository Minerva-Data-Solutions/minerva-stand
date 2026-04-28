from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from urllib import error, parse, request

from config import BaserowConfig


@dataclass(frozen=True)
class APIResult:
    status: int
    body: str

    def json(self) -> Any:
        if not self.body:
            return None
        try:
            return json.loads(self.body)
        except json.JSONDecodeError:
            return {"raw": self.body}


@dataclass
class BaserowClient:
    config: BaserowConfig

    def _headers(self, auth_scheme: str | None, token: str | None, json_body: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if auth_scheme and token:
            headers["Authorization"] = f"{auth_scheme} {token}"
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _request_raw(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        query: dict | None = None,
        auth_scheme: str | None = None,
        token: str | None = None,
    ) -> APIResult:
        url = self.config.base_url.rstrip("/") + path
        if query:
            url += "?" + parse.urlencode(query)
        data = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            headers=self._headers(auth_scheme, token, json_body=payload is not None),
            method=method,
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                return APIResult(resp.status, resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            return APIResult(exc.code, exc.read().decode("utf-8", errors="replace"))
        except error.URLError as exc:
            body = json.dumps({"error": "URL_ERROR", "description": str(exc.reason)}, sort_keys=True)
            return APIResult(599, body)

    def _database_token(self, account_name: str) -> str:
        if account_name not in self.config.accounts:
            raise KeyError(f"Unknown Baserow account: {account_name}")
        return self.config.accounts[account_name].token

    def _refresh_jwt_access_token(self) -> APIResult:
        if not self.config.jwt_refresh_token:
            body = json.dumps(
                {"error": "MISSING_JWT_REFRESH_TOKEN", "description": "BASEROW_JWT_REFRESH_TOKEN is required for schema operations."},
                sort_keys=True,
            )
            return APIResult(401, body)
        result = self._request_raw(
            "POST",
            "/api/user/token-refresh/",
            payload={"refresh_token": self.config.jwt_refresh_token},
        )
        if result.status >= 400:
            return result
        data = result.json()
        token = data.get("access_token") or data.get("token")
        if not token:
            body = json.dumps(
                {"error": "MISSING_ACCESS_TOKEN", "description": "Baserow refresh response did not include an access token."},
                sort_keys=True,
            )
            return APIResult(502, body)
        return APIResult(200, json.dumps({"access_token": token}, sort_keys=True))

    def _jwt_access_token(self) -> APIResult:
        if self.config.jwt_access_token:
            return APIResult(200, json.dumps({"access_token": self.config.jwt_access_token}, sort_keys=True))
        return self._refresh_jwt_access_token()

    def row_request(
        self,
        account_name: str,
        method: str,
        path: str,
        payload: dict | None = None,
        query: dict | None = None,
    ) -> APIResult:
        token = self._database_token(account_name)
        if not token:
            body = json.dumps({"error": "MISSING_DATABASE_TOKEN", "description": f"Missing token for account {account_name}."}, sort_keys=True)
            return APIResult(401, body)
        return self._request_raw(method, path, payload=payload, query=query, auth_scheme="Token", token=token)

    def schema_request(
        self,
        method: str,
        path: str,
        payload: dict | None = None,
        query: dict | None = None,
    ) -> APIResult:
        body = json.dumps(
            {
                "description": "JWT-backed schema operations are intentionally unavailable in this skill for now.",
                "error": "SCHEMA_OPERATIONS_UNAVAILABLE",
                "method": method,
                "path": path,
            },
            sort_keys=True,
        )
        return APIResult(501, body)

    def request(self, account_name: str, method: str, path: str, payload: dict | None = None, query: dict | None = None) -> APIResult:
        return self.row_request(account_name, method, path, payload=payload, query=query)

    def list_workspaces(self) -> APIResult:
        return self.schema_request("GET", "/api/workspaces/")

    def list_databases(self) -> APIResult:
        return self.schema_request("GET", "/api/applications/", query={"type": "database"})

    def list_all_tables(self, account_name: str) -> APIResult:
        return self.row_request(account_name, "GET", "/api/database/tables/all-tables/")

    def list_database_tables(self, database_id: int | str) -> APIResult:
        return self.schema_request("GET", f"/api/database/tables/database/{database_id}/")

    def list_database_tables_with_token(self, account_name: str, database_id: int | str) -> APIResult:
        result = self.list_all_tables(account_name)
        if result.status >= 400:
            return result
        tables = [table for table in result.json() if str(table.get("database_id")) == str(database_id)]
        return APIResult(200, json.dumps(tables, sort_keys=True))

    def list_table_fields(self, account_name: str, table_id: int | str) -> APIResult:
        return self.row_request(account_name, "GET", f"/api/database/fields/table/{table_id}/")

    def list_rows(
        self,
        account_name: str,
        table_id: int | str,
        user_field_names: bool = True,
        page: int | None = None,
        size: int | None = None,
        search: str | None = None,
        order_by: str | None = None,
        filters: dict | None = None,
    ) -> APIResult:
        query: dict[str, Any] = {"user_field_names": str(user_field_names).lower()}
        if page is not None:
            query["page"] = page
        if size is not None:
            query["size"] = size
        if search:
            query["search"] = search
        if order_by:
            query["order_by"] = order_by
        if filters is not None:
            query["filters"] = json.dumps(filters, sort_keys=True)
        return self.row_request(account_name, "GET", f"/api/database/rows/table/{table_id}/", query=query)

    def get_row(self, account_name: str, table_id: int | str, row_id: int | str, user_field_names: bool = True) -> APIResult:
        return self.row_request(account_name, "GET", f"/api/database/rows/table/{table_id}/{row_id}/", query={"user_field_names": str(user_field_names).lower()})

    def create_row(self, account_name: str, table_id: int | str, payload: dict, user_field_names: bool = True) -> APIResult:
        return self.row_request(account_name, "POST", f"/api/database/rows/table/{table_id}/", payload=payload, query={"user_field_names": str(user_field_names).lower()})

    def update_row(self, account_name: str, table_id: int | str, row_id: int | str, payload: dict, user_field_names: bool = True) -> APIResult:
        return self.row_request(account_name, "PATCH", f"/api/database/rows/table/{table_id}/{row_id}/", payload=payload, query={"user_field_names": str(user_field_names).lower()})

    def delete_row(self, account_name: str, table_id: int | str, row_id: int | str) -> APIResult:
        return self.row_request(account_name, "DELETE", f"/api/database/rows/table/{table_id}/{row_id}/")

    def create_table(self, database_id: int | str, payload: dict) -> APIResult:
        return self.schema_request("POST", f"/api/database/tables/database/{database_id}/", payload=payload)

    def update_table(self, table_id: int | str, payload: dict) -> APIResult:
        return self.schema_request("PATCH", f"/api/database/tables/{table_id}/", payload=payload)

    def delete_table(self, table_id: int | str) -> APIResult:
        return self.schema_request("DELETE", f"/api/database/tables/{table_id}/")

    def create_field(self, table_id: int | str, payload: dict) -> APIResult:
        return self.schema_request("POST", f"/api/database/fields/table/{table_id}/", payload=payload)

    def get_field(self, field_id: int | str) -> APIResult:
        return self.schema_request("GET", f"/api/database/fields/{field_id}/")

    def update_field(self, field_id: int | str, payload: dict) -> APIResult:
        return self.schema_request("PATCH", f"/api/database/fields/{field_id}/", payload=payload)

    def delete_field(self, field_id: int | str) -> APIResult:
        return self.schema_request("DELETE", f"/api/database/fields/{field_id}/")
