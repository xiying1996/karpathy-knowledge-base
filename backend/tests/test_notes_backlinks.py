"""
测试 notes 路由的 backlinks 相关 API：
1. GET /api/notes/{note_id} 返回 backlinks 字段
2. GET /api/notes/{note_id}/backlinks 返回 backlinks 列表
3. 404 场景

使用 FastAPI dependency_overrides 注入测试 VaultReader/BacklinksService。
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.vault_reader import VaultReader, get_vault_reader
from app.services.backlinks import BacklinksService, get_backlinks


@pytest.fixture
def client(vault_with_notes, kkb_dir):
    """
    使用 dependency_overrides 将生产 VaultReader/BacklinksService
    替换为指向 vault_with_notes 的测试实例。
    """
    test_vault = str(vault_with_notes)

    test_vault_reader = VaultReader(test_vault)
    test_backlinks = BacklinksService(
        vault_path=test_vault,
        index_path=kkb_dir / "backlinks.json",
    )
    test_backlinks.rebuild_full_index()

    app.dependency_overrides[get_vault_reader] = lambda: test_vault_reader
    app.dependency_overrides[get_backlinks] = lambda: test_backlinks

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


def test_get_note_includes_backlinks(client):
    """GET /api/notes/{note_id} 返回 NoteWithBacklinks 包含 backlinks 字段"""
    response = client.get("/api/notes/Note-A")
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()

    assert "backlinks" in data
    assert isinstance(data["backlinks"], list)
    assert len(data["backlinks"]) == 1
    assert data["backlinks"][0]["id"] == "Note-D"
    assert data["backlinks"][0]["title"] == "Note D"


def test_get_note_backlinks_endpoint(client):
    """GET /api/notes/{note_id}/backlinks 返回 backlinks 列表"""
    response = client.get("/api/notes/Note-C/backlinks")
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    data = response.json()

    assert isinstance(data, list)
    ids = {item["id"] for item in data}
    assert ids == {"Note-A", "Note-B", "Note-D"}


def test_get_note_no_backlinks(client):
    """GET /api/notes/{note_id} 笔记无 backlinks 时返回空列表"""
    response = client.get("/api/notes/Note-D")
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    assert response.json()["backlinks"] == []


def test_get_note_not_found(client):
    """笔记不存在返回 404"""
    response = client.get("/api/notes/non-existent-note")
    assert response.status_code == 404


def test_backlinks_endpoint_not_found(client):
    """GET /api/notes/{note_id}/backlinks 笔记不存在返回 404"""
    response = client.get("/api/notes/non-existent-note/backlinks")
    assert response.status_code == 404
