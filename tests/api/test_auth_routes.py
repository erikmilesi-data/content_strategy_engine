# tests/api/test_auth_routes.py
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_login_admin_sucesso(client: TestClient):
    payload = {"username": "admin", "password": "admin123"}

    resp = client.post("/api/auth/login", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "admin"


@pytest.mark.api
def test_login_credenciais_invalidas(client: TestClient):
    payload = {"username": "admin", "password": "senha_errada"}

    resp = client.post("/api/auth/login", json=payload)

    assert resp.status_code == 401
    data = resp.json()
    assert data["detail"] == "Credenciais inválidas"
