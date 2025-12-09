# tests/api/test_content_strategy_routes.py
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_generate_content_strategy_com_dados_basicos(
    client: TestClient, auth_headers: dict
):
    """
    Teste de integração da rota /api/content/strategy.

    Fluxo:
    - Usa token do admin
    - Envia um payload simples de ContentStrategyRequest
    - Verifica estrutura básica da resposta
    """
    payload = {
        "topic": "Consultoria de imagem para mães",
        "platform": "instagram",
        "mode": "rich",
        "users": [
            {"age": 32, "gender": "female", "region": "Rio de Janeiro"},
            {"age": 28, "gender": "female", "region": "São Paulo"},
        ],
        "project_id": None,
    }

    resp = client.post(
        "/api/content/strategy",
        json=payload,
        headers=auth_headers,
    )

    # Se algo der 500 aqui, é bug de regra de negócio / dependência
    assert resp.status_code == 200, resp.text

    data = resp.json()

    # Checagens básicas de contrato
    assert data["topic"] == payload["topic"]
    assert data["platform"] == payload["platform"]
    assert data["mode"] == payload["mode"]

    assert "audience" in data
    assert "suggestions" in data
    assert "best_times" in data

    # audience deve ter summary/profiles/dominant_profile (ver content_strategy.py)
    audience = data["audience"]
    assert "summary" in audience
    assert "profiles" in audience
    assert "dominant_profile" in audience


@pytest.mark.api
def test_get_history_requer_autenticacao(client: TestClient):
    """
    /api/content/history deve exigir token.
    """
    resp = client.get("/api/content/history")
    assert resp.status_code in (401, 403)


@pytest.mark.api
def test_get_history_filtra_por_usuario_logado(client: TestClient, auth_headers: dict):
    """
    Garante que a rota de histórico responde 200 para usuário autenticado
    e retorna um dict com chave 'history'.
    """
    resp = client.get("/api/content/history", headers=auth_headers)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "history" in data
    assert isinstance(data["history"], list)
