import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.deps import build_mock_services, get_services
from app.main import app


@pytest.fixture
def ctx():
    svc = build_mock_services(Settings.from_env())
    app.dependency_overrides[get_services] = lambda: svc
    yield TestClient(app), svc
    app.dependency_overrides.clear()


def test_health_reports_mock(ctx):
    client, _ = ctx
    assert client.get("/health").json() == {"status": "ok", "backend": "mock"}


def test_upload_hits_all_three_services(ctx):
    client, svc = ctx
    res = client.post("/files", files={"file": ("hello.txt", b"hi there", "text/plain")})
    assert res.status_code == 201
    body = res.json()
    assert body["size_bytes"] == 8

    assert len(svc.storage.objects) == 1          # Cloud Storage
    assert len(svc.warehouse.rows) == 1           # BigQuery
    assert svc.publisher.messages[0]["data"]["event"] == "file.uploaded"  # Pub/Sub


def test_empty_file_rejected(ctx):
    client, svc = ctx
    res = client.post("/files", files={"file": ("empty.txt", b"", "text/plain")})
    assert res.status_code == 400
    assert not svc.storage.objects


def test_list_and_events(ctx):
    client, _ = ctx
    client.post("/files", files={"file": ("a.txt", b"aaa", "text/plain")})
    client.post("/files", files={"file": ("b.txt", b"bbb", "text/plain")})
    assert len(client.get("/files").json()["files"]) == 2
    assert len(client.get("/events?limit=1").json()) == 1
