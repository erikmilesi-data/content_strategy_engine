# tests/api/test_projects_routes.py
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_listar_projetos_sem_autenticacao(client: TestClient):
    """
    /api/projects/ deve exigir token. Sem Authorization → 401/403.
    """
    response = client.get("/api/projects/")
    assert response.status_code in (401, 403)


@pytest.mark.api
def test_criar_projeto_com_dados_validos(client: TestClient, auth_headers: dict):
    """
    Cria um projeto válido com usuário autenticado (admin/admin123).
    """
    payload = {
        "name": "Projeto de Teste",
        "description": "Projeto criado via teste automatizado",
        "ig_user_id": "17841400000000000",
    }

    response = client.post(
        "/api/projects/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code in (200, 201), response.text
    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    # owner_id é preenchido pelo backend a partir do usuário logado
    assert "id" in data
    assert "owner_id" in data
