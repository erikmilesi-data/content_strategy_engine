# tests/conftest.py
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Client HTTP para testar a API completa.

    O próprio app, no evento de startup, já chama:
      - init_db_sqlmodel()  -> cria content_strategy_sqlmodel.db
      - init_history_db()   -> cria history.db + usuário admin/admin123
    """
    test_client = TestClient(app)
    yield test_client


@pytest.fixture(scope="session")
def auth_headers(client: TestClient) -> dict:
    """
    Faz login com o usuário admin criado em src/database/db.py
    e devolve o header Authorization pronto pra uso.
    """
    login_payload = {
        "username": "admin",
        "password": "admin123",
    }
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, f"Falha no login admin: {resp.text}"

    data = resp.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}
