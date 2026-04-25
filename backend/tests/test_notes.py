import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client(tmp_path):
    """返回使用测试 vault 的 TestClient，覆盖 get_vault_reader 依赖。"""
    vault = tmp_path / "vault"
    vault.mkdir()
    demo = vault / "demo"
    demo.mkdir()

    # 创建真实测试数据，匹配 vault/demo/ 下的笔记结构
    (demo / "2026-04-24.md").write_text(
        "---\ntitle: Test Note\ndate: 2026-04-24\n---\n# Test Note\n\nContent of test note.\n",
        encoding="utf-8",
    )
    (demo / "第二大脑.md").write_text(
        "---\ntitle: 第二大脑\ndate: 2026-04-20\n---\n# 第二大脑\n\n这是关于第二大脑的笔记。\n",
        encoding="utf-8",
    )

    from app.services.vault_reader import VaultReader, get_vault_reader
    test_reader = VaultReader(str(vault))
    app.dependency_overrides[get_vault_reader] = lambda: test_reader

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


def test_list_notes_returns_non_empty(client):
    response = client.get("/api/notes")
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert "total" in data
    assert data["total"] > 0


def test_get_note_by_id(client):
    response = client.get("/api/notes/2026-04-24")
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["id"] == "2026-04-24"
    assert len(data["content"]) > 0


def test_get_note_404(client):
    response = client.get("/api/notes/nonexistent")
    assert response.status_code == 404


def test_list_notes_with_search(client):
    response = client.get("/api/notes?search=第二大脑")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_list_notes_with_no_match(client):
    response = client.get("/api/notes?search=xyznonexistent123")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0