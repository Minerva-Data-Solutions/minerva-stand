from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import aiosqlite
from aiohttp import web
from loguru import logger

from nanobot.api.server import API_CHAT_ID, _error_json, _response_text

_SESSION_COOKIE = "minerva_wb"
_MAX_BODY = 2_000_000
_QUERY_TIMEOUT_MS = 30_000


@dataclass(frozen=True)
class WorkbenchRuntime:
    workspace_root: Path
    audit_db_path: Path
    username: str
    password: str
    secret: str
    cors_origins: frozenset[str]
    agent_loop: Any
    model_name: str
    request_timeout: float


def load_workbench_runtime(
    *,
    workspace_root: Path,
    audit_db_path: Path,
    agent_loop: Any,
    model_name: str,
    request_timeout: float,
) -> WorkbenchRuntime | None:
    username = (os.environ.get("MINERVA_UI_USER") or "").strip()
    password = os.environ.get("MINERVA_UI_PASSWORD") or ""
    if not username or not password:
        return None
    secret = (os.environ.get("MINERVA_UI_SECRET") or "").strip()
    if not secret:
        secret = hashlib.sha256(f"{username}\x00{password}".encode()).hexdigest()
    _default_cors = ",".join(
        f"{host}:{port}"
        for host in ("http://127.0.0.1", "http://localhost")
        for port in ("5174", "5173", "4173", "3000")
    )
    raw = os.environ.get("MINERVA_UI_CORS_ORIGINS", _default_cors)
    origins = frozenset(x.strip() for x in raw.split(",") if x.strip())
    return WorkbenchRuntime(
        workspace_root=workspace_root.resolve(),
        audit_db_path=audit_db_path.expanduser().resolve(),
        username=username,
        password=password,
        secret=secret,
        cors_origins=origins,
        agent_loop=agent_loop,
        model_name=model_name,
        request_timeout=request_timeout,
    )


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _sign(secret: str, payload: str) -> str:
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return _b64url(sig)


def _make_token(secret: str, exp: int) -> str:
    payload = json.dumps({"exp": exp, "v": 1}, separators=(",", ":"))
    p_b64 = _b64url(payload.encode())
    sig = _sign(secret, p_b64)
    return f"{p_b64}.{sig}"


def _parse_token(secret: str, token: str) -> dict[str, Any] | None:
    try:
        p_b64, sig = token.split(".", 1)
    except ValueError:
        return None
    if _sign(secret, p_b64) != sig:
        return None
    pad = "=" * (-len(p_b64) % 4)
    raw = base64.urlsafe_b64decode(p_b64 + pad)
    data = json.loads(raw.decode("utf-8"))
    if int(data.get("exp", 0)) < int(time.time()):
        return None
    return data


def _cors_headers(request: web.Request, rt: WorkbenchRuntime) -> dict[str, str]:
    origin = request.headers.get("Origin")
    if origin and (origin in rt.cors_origins or "*" in rt.cors_origins):
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        }
    return {}


@web.middleware
async def workbench_cors_middleware(request: web.Request, handler):
    rt: WorkbenchRuntime | None = request.app.get("workbench")
    if rt is None:
        return await handler(request)
    if request.method == "OPTIONS":
        h = _cors_headers(request, rt)
        if not h:
            return web.Response(status=204)
        return web.Response(status=204, headers=h)
    resp = await handler(request)
    if isinstance(resp, web.StreamResponse):
        h = _cors_headers(request, rt)
        for k, v in h.items():
            resp.headers[k] = v
    return resp


def _safe_under_root(root: Path, rel: str) -> Path | None:
    if rel.strip() != rel:
        return None
    s = rel.strip()
    root = root.resolve()
    if not s:
        return root
    parts = Path(s.replace("\\", "/")).parts
    if ".." in parts or parts[:1] == ("/",):
        return None
    candidate = (root / s).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


_SELECT_OK = re.compile(
    r"^\s*(WITH|SELECT)\b",
    re.IGNORECASE | re.DOTALL,
)


def _sql_allowed(sql: str) -> bool:
    s = sql.strip()
    if not s or len(s) > 100_000:
        return False
    if ";" in s.rstrip().rstrip(";"):
        return False
    if not _SELECT_OK.match(s):
        return False
    lowered = s.lower()
    for bad in (
        "attach ",
        "detach ",
        "pragma write",
        "pragma journal_mode",
        "pragma locking_mode",
    ):
        if bad in lowered:
            return False
    return True


async def handle_workbench_login(request: web.Request) -> web.Response:
    rt: WorkbenchRuntime = request.app["workbench"]
    try:
        body = await request.json()
    except Exception:
        return _error_json(400, "Invalid JSON body")
    user = body.get("username") if isinstance(body.get("username"), str) else ""
    pw = body.get("password") if isinstance(body.get("password"), str) else ""
    if not secrets.compare_digest(user, rt.username) or not secrets.compare_digest(pw, rt.password):
        return _error_json(401, "Invalid credentials")
    exp = int(time.time()) + 7 * 24 * 3600
    token = _make_token(rt.secret, exp)
    resp = web.json_response({"ok": True})
    resp.set_cookie(
        _SESSION_COOKIE,
        token,
        httponly=True,
        samesite="Lax",
        max_age=7 * 24 * 3600,
        path="/",
    )
    return resp


async def handle_workbench_logout(request: web.Request) -> web.Response:
    resp = web.json_response({"ok": True})
    resp.del_cookie(_SESSION_COOKIE, path="/")
    return resp


async def handle_workbench_session(request: web.Request) -> web.Response:
    token = request.cookies.get(_SESSION_COOKIE)
    rt: WorkbenchRuntime = request.app["workbench"]
    if not token or _parse_token(rt.secret, token) is None:
        return _error_json(401, "Unauthorized")
    return web.json_response({"authenticated": True})


def _require_wb_auth(request: web.Request) -> web.Response | None:
    token = request.cookies.get(_SESSION_COOKIE)
    rt: WorkbenchRuntime = request.app["workbench"]
    if not token or _parse_token(rt.secret, token) is None:
        return _error_json(401, "Unauthorized")
    return None


async def handle_workbench_chat(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    try:
        body = await request.json()
    except Exception:
        return _error_json(400, "Invalid JSON body")
    content = body.get("message") if isinstance(body.get("message"), str) else ""
    if not content.strip():
        return _error_json(400, "message required")
    session_key = body.get("sessionId") if isinstance(body.get("sessionId"), str) else "api:default"
    if not session_key.startswith("api:"):
        session_key = f"api:{session_key}"
    agent_loop = rt.agent_loop
    timeout_s = rt.request_timeout
    session_locks: dict = request.app["session_locks"]
    lock = session_locks.setdefault(session_key, asyncio.Lock())

    try:
        async with lock:
            response = await asyncio.wait_for(
                agent_loop.process_direct(
                    content=content,
                    session_key=session_key,
                    channel="api",
                    chat_id=API_CHAT_ID,
                ),
                timeout=timeout_s,
            )
            text = _response_text(response)
    except asyncio.TimeoutError:
        return _error_json(504, f"Request timed out after {timeout_s}s")
    except Exception:
        logger.exception("workbench chat error")
        return _error_json(500, "Internal server error", err_type="server_error")
    return web.json_response({"reply": text})


async def handle_workbench_files_list(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    rel = request.query.get("path", "") or ""
    root = rt.workspace_root.resolve()
    target = _safe_under_root(root, rel)
    if target is None:
        return _error_json(400, "Invalid path")
    if not target.exists():
        return _error_json(404, "Not found")
    if target.is_file():
        return web.json_response(
            {
                "type": "file",
                "name": target.name,
                "path": rel,
                "size": target.stat().st_size,
            }
        )
    entries = []
    try:
        for child in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            rel_child = str(Path(rel) / child.name) if rel else child.name
            st = child.stat()
            entries.append(
                {
                    "name": child.name,
                    "path": rel_child.replace("\\", "/"),
                    "isDir": child.is_dir(),
                    "size": st.st_size if child.is_file() else None,
                }
            )
    except OSError as e:
        return _error_json(500, str(e))
    return web.json_response({"type": "directory", "path": rel or "", "entries": entries})


async def handle_workbench_files_read(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    rel = request.query.get("path", "") or ""
    root = rt.workspace_root.resolve()
    target = _safe_under_root(root, rel)
    if target is None:
        return _error_json(400, "Invalid path")
    if not target.is_file():
        return _error_json(400, "Not a file")
    try:
        data = target.read_bytes()
    except OSError as e:
        return _error_json(500, str(e))
    if len(data) > _MAX_BODY:
        return _error_json(413, "File too large")
    try:
        text = data.decode("utf-8")
        binary = False
    except UnicodeDecodeError:
        text = base64.b64encode(data).decode("ascii")
        binary = True
    return web.json_response({"path": rel, "text": text, "binary": binary})


async def handle_workbench_files_write(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    try:
        body = await request.json()
    except Exception:
        return _error_json(400, "Invalid JSON body")
    rel = body.get("path") if isinstance(body.get("path"), str) else ""
    content = body.get("content") if isinstance(body.get("content"), str) else None
    if content is None or rel is None:
        return _error_json(400, "path and content required")
    if len(content.encode("utf-8")) > _MAX_BODY:
        return _error_json(413, "Payload too large")
    root = rt.workspace_root.resolve()
    target = _safe_under_root(root, rel)
    if target is None:
        return _error_json(400, "Invalid path")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as e:
        return _error_json(500, str(e))
    return web.json_response({"ok": True})


async def handle_workbench_sqlite_tables(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    db_path = rt.audit_db_path.expanduser().resolve()
    if not db_path.is_file():
        return web.json_response({"tables": []})
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cur = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            rows = await cur.fetchall()
    except Exception:
        logger.exception("sqlite tables")
        return _error_json(500, "Database error")
    return web.json_response({"tables": [r["name"] for r in rows]})


async def handle_workbench_sqlite_query(request: web.Request) -> web.Response:
    err = _require_wb_auth(request)
    if err:
        return err
    rt: WorkbenchRuntime = request.app["workbench"]
    try:
        body = await request.json()
    except Exception:
        return _error_json(400, "Invalid JSON body")
    sql = body.get("sql") if isinstance(body.get("sql"), str) else ""
    if not _sql_allowed(sql):
        return _error_json(400, "Only single SELECT / WITH queries are allowed")
    db_path = rt.audit_db_path.expanduser().resolve()
    if not db_path.is_file():
        return _error_json(404, "Audit database not found")
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute(f"PRAGMA busy_timeout={_QUERY_TIMEOUT_MS}")
            cur = await conn.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = await cur.fetchall()
            data = [{cols[i]: row[i] for i in range(len(cols))} for row in rows]
            if len(data) > 5000:
                data = data[:5000]
                truncated = True
            else:
                truncated = False
    except Exception as e:
        logger.warning("sqlite query: {}", e)
        return _error_json(400, str(e))
    return web.json_response({"columns": cols, "rows": data, "truncated": truncated})


def register_workbench_routes(app: web.Application, rt: WorkbenchRuntime) -> None:
    app["workbench"] = rt
    app.middlewares.append(workbench_cors_middleware)
    app.router.add_post("/api/workbench/auth/login", handle_workbench_login)
    app.router.add_post("/api/workbench/auth/logout", handle_workbench_logout)
    app.router.add_get("/api/workbench/auth/session", handle_workbench_session)
    app.router.add_post("/api/workbench/chat", handle_workbench_chat)
    app.router.add_get("/api/workbench/files", handle_workbench_files_list)
    app.router.add_get("/api/workbench/files/content", handle_workbench_files_read)
    app.router.add_put("/api/workbench/files/content", handle_workbench_files_write)
    app.router.add_get("/api/workbench/sqlite/tables", handle_workbench_sqlite_tables)
    app.router.add_post("/api/workbench/sqlite/query", handle_workbench_sqlite_query)
