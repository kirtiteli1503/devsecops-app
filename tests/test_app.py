import pytest

from app.main import create_app


@pytest.fixture()
def client():
    app = create_app("sqlite:///:memory:")
    app.testing = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_create_and_get_note(client):
    r = client.post("/notes", json={"title": "First", "body": "hello"})
    assert r.status_code == 201
    note_id = r.get_json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.get_json()["title"] == "First"


def test_create_note_requires_title(client):
    r = client.post("/notes", json={"body": "no title"})
    assert r.status_code == 400


def test_list_notes(client):
    client.post("/notes", json={"title": "A"})
    client.post("/notes", json={"title": "B"})
    r = client.get("/notes")
    assert [n["title"] for n in r.get_json()] == ["A", "B"]


def test_delete_note(client):
    note_id = client.post("/notes", json={"title": "Temp"}).get_json()["id"]
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404
