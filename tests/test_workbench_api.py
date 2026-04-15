"""Tests for Minerva Workbench API routes."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from nanobot.api.server import create_app
from nanobot.api.workbench import load_workbench_runtime

try:
    from aiohttp.test_utils import TestClient, TestServer

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

pytest_plugins = ("pytest_asyncio",)


def _mock_agent() -> MagicMock:
    agent = MagicMock()
    agent.process_direct = AsyncMock(return_value="ok")
    return agent


@pytest_asyncio.fixture
async def aiohttp_client():
    clients: list[TestClient] = []

    async def _make_client(app):
        client = TestClient(TestServer(app))
        await client.start_server()
        clients.append(client)
        return client

    try:
        yield _make_client
    finally:
        for client in clients:
            await client.close()


@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
@pytest.mark.asyncio
async def test_workbench_login_session_and_files(
    aiohttp_client, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MINERVA_UI_USER", "u1")
    monkeypatch.setenv("MINERVA_UI_PASSWORD", "p1")
    monkeypatch.setenv("MINERVA_UI_SECRET", "fixedsecret")
    monkeypatch.setenv("MINERVA_UI_CORS_ORIGINS", "http://localhost:5174")

    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "readme.md").write_text("hello", encoding="utf-8")
    audit = tmp_path / "agent_audit.db"

    agent = _mock_agent()
    wb = load_workbench_runtime(
        workspace_root=ws,
        audit_db_path=audit,
        agent_loop=agent,
        model_name="m",
        request_timeout=10.0,
    )
    assert wb is not None

    app = create_app(agent, model_name="m", request_timeout=10.0, workbench=wb)
    client = await aiohttp_client(app)

    bad = await client.post(
        "/api/workbench/auth/login",
        json={"username": "u1", "password": "wrong"},
    )
    assert bad.status == 401

    good = await client.post(
        "/api/workbench/auth/login",
        json={"username": "u1", "password": "p1"},
    )
    assert good.status == 200
    cookie = good.cookies.get("minerva_wb")
    assert cookie is not None

    sess = await client.get("/api/workbench/auth/session", cookies={"minerva_wb": cookie.value})
    assert sess.status == 200
    assert (await sess.json()).get("authenticated") is True

    listed = await client.get("/api/workbench/files", cookies={"minerva_wb": cookie.value})
    assert listed.status == 200
    body = await listed.json()
    assert body["type"] == "directory"
    names = {e["name"] for e in body["entries"]}
    assert "readme.md" in names

    content = await client.get(
        "/api/workbench/files/content?path=readme.md",
        cookies={"minerva_wb": cookie.value},
    )
    assert content.status == 200
    cj = await content.json()
    assert cj["text"] == "hello"
    assert cj["binary"] is False


@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
@pytest.mark.asyncio
async def test_workbench_sqlite_select(
    aiohttp_client, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MINERVA_UI_USER", "u1")
    monkeypatch.setenv("MINERVA_UI_PASSWORD", "p1")
    monkeypatch.setenv("MINERVA_UI_SECRET", "fixedsecret")

    import aiosqlite

    ws = tmp_path / "ws"
    ws.mkdir()
    audit = tmp_path / "db.sqlite"
    async with aiosqlite.connect(audit) as conn:
        await conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
        await conn.execute("INSERT INTO t (name) VALUES ('x')")
        await conn.commit()

    agent = _mock_agent()
    wb = load_workbench_runtime(
        workspace_root=ws,
        audit_db_path=audit,
        agent_loop=agent,
        model_name="m",
        request_timeout=10.0,
    )
    app = create_app(agent, workbench=wb)
    client = await aiohttp_client(app)

    login = await client.post(
        "/api/workbench/auth/login",
        json={"username": "u1", "password": "p1"},
    )
    ck = login.cookies.get("minerva_wb")

    tabs = await client.get("/api/workbench/sqlite/tables", cookies={"minerva_wb": ck.value})
    assert await tabs.json() == {"tables": ["t"]}

    q = await client.post(
        "/api/workbench/sqlite/query",
        json={"sql": "SELECT id, name FROM t"},
        cookies={"minerva_wb": ck.value},
    )
    assert q.status == 200
    qj = await q.json()
    assert qj["columns"] == ["id", "name"]
    assert qj["rows"] == [{"id": 1, "name": "x"}]

    bad = await client.post(
        "/api/workbench/sqlite/query",
        json={"sql": "DELETE FROM t"},
        cookies={"minerva_wb": ck.value},
    )
    assert bad.status == 400
