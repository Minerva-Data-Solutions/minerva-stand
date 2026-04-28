from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any
from urllib import error, parse, request


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
class BaserowAPI:
    base_url: str

    def request(
        self,
        token: str,
        method: str,
        path: str,
        payload: dict | None = None,
        query: dict | None = None,
        auth_scheme: str = "Token",
    ) -> APIResult:
        if not token.strip():
            body = json.dumps(
                {"error": "MISSING_DATABASE_TOKEN", "description": "No Baserow database token was provided."},
                sort_keys=True,
            )
            return APIResult(401, body)
        url = self.base_url.rstrip("/") + path
        if query:
            url += "?" + parse.urlencode(query)
        headers = {
            "Authorization": f"{auth_scheme} {token}",
            "Content-Type": "application/json",
        }
        data = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=30) as response:
                return APIResult(response.status, response.read().decode("utf-8"))
        except error.HTTPError as exc:
            return APIResult(exc.code, exc.read().decode("utf-8", errors="replace"))
