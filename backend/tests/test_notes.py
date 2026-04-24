from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_list_notes_returns_non_empty():
    response = client.get("/api/notes")
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert "total" in data
    assert data["total"] > 0


def test_get_note_by_id():
    response = client.get("/api/notes/2026-04-24")
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert data["id"] == "2026-04-24"
    assert len(data["content"]) > 0


def test_get_note_404():
    response = client.get("/api/notes/nonexistent")
    assert response.status_code == 404


def test_list_notes_with_search():
    response = client.get("/api/notes?search=第二大脑")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_list_notes_with_no_match():
    response = client.get("/api/notes?search=xyznonexistent123")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0