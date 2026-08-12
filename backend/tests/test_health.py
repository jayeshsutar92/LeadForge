import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, base_url="http://localhost/")


def test_liveness():
    response = client.get("/api/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
