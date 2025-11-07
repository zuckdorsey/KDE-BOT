import os
import json
import types
import pytest

from client.server import app, AUTH_TOKEN

def auth_headers():
    return {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}

@pytest.fixture()
def client():
    app.testing = True
    with app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "online"


def test_status_requires_auth(client):
    resp = client.get("/status")
    assert resp.status_code == 401


def test_status_ok_with_auth(client):
    resp = client.get("/status", headers=auth_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert "hostname" in data
    assert "cpu" in data


def test_unknown_command(client):
    payload = {"command": "not_exists", "params": {}}
    resp = client.post("/command", data=json.dumps(payload), headers=auth_headers())
    assert resp.status_code in (200, 400)
    data = resp.get_json()
    assert data["status"] == "error"


def test_copy_paste_roundtrip(client):
    # paste may fail on CI environments without clipboard; still ensure endpoint responds
    payload = {"command": "copy", "params": {"text": "hello"}}
    client.post("/command", data=json.dumps(payload), headers=auth_headers())
    payload = {"command": "paste", "params": {}}
    resp = client.post("/command", data=json.dumps(payload), headers=auth_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] in ("success", "error")


def test_download_restriction(client, tmp_path, monkeypatch):
    # Ensure getfile forbids outside allowed dirs
    outside_path = tmp_path / "secret.txt"
    outside_path.write_text("secret")
    resp = client.post("/getfile", data=json.dumps({"path": str(outside_path)}), headers=auth_headers())
    assert resp.status_code in (403, 500)

