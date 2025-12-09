# tests/test_health.py
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_ok():
    """Verifica se o endpoint /health está respondendo corretamente."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
