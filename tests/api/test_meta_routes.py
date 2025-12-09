# tests/api/test_meta_routes.py
import pytest
from fastapi.testclient import TestClient


class DummyMetaClient:
    """
    Mock simples para substituir o MetaClient real durante os testes.

    Ele imita a interface de:
      - publish_image(...)
      - get_ig_insights(...)
    """

    def publish_image(
        self,
        ig_user_id: str,
        image_url: str,
        caption: str = "",
        project_id=None,
        username=None,
    ):
        return {
            "step": "done",
            "status_code": 200,
            "creation_id": "1234567890",
            "publish_result": {"id": "1234567890", "caption": caption},
            "ig_user_id": ig_user_id,
            "image_url": image_url,
            "project_id": project_id,
            "username": username,
        }

    def get_ig_insights(self, ig_business_account_id: str, since=None, until=None):
        return {
            "time_series": {
                "status_code": 200,
                "body": {"data": []},
                "step": "time_series",
            },
            "total_value": {
                "status_code": 200,
                "body": {"data": []},
                "step": "total_value",
            },
            "demographics": {
                "status_code": 200,
                "body": {"data": []},
                "step": "demographics",
            },
            "snapshot": {
                "status_code": 200,
                "body": {"followers_count": 1000, "media_count": 50},
                "step": "snapshot",
            },
            "ig_business_account_id": ig_business_account_id,
            "since": since,
            "until": until,
        }


@pytest.fixture
def patched_meta_client(monkeypatch):
    """
    Substitui o meta_client global do módulo src.api.routes.meta
    por um DummyMetaClient durante os testes.
    """
    from src.api.routes import meta as meta_routes

    dummy = DummyMetaClient()
    monkeypatch.setattr(meta_routes, "meta_client", dummy)
    return dummy


@pytest.mark.api
def test_publish_instagram_image_sucesso(
    client: TestClient, auth_headers: dict, patched_meta_client: DummyMetaClient
):
    payload = {
        "ig_user_id": "17841400000000000",
        "image_url": "https://exemplo.com/imagem-teste.jpg",
        "caption": "Post de teste via StratifyAI",
        "project_id": 42,
    }

    resp = client.post(
        "/api/meta/instagram/publish-image",
        json=payload,
        headers=auth_headers,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["message"] == "Publicação realizada com sucesso no Instagram."
    assert data["user"] == "admin"
    assert data["project_id"] == 42

    meta_result = data["meta_result"]
    assert meta_result["status_code"] == 200
    assert meta_result["ig_user_id"] == payload["ig_user_id"]
    assert meta_result["image_url"] == payload["image_url"]
    assert meta_result["publish_result"]["caption"] == payload["caption"]


@pytest.mark.api
def test_get_instagram_insights_sucesso(
    client: TestClient, auth_headers: dict, patched_meta_client: DummyMetaClient
):
    params = {
        "ig_business_account_id": "17841400000000000",
        "since": "2024-10-01",
        "until": "2024-10-07",
    }

    resp = client.get(
        "/api/meta/instagram/insights",
        params=params,
        headers=auth_headers,
    )

    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["message"] == "Consulta de insights concluída com sucesso."
    assert data["user"] == "admin"

    meta_result = data["meta_result"]
    assert "time_series" in meta_result
    assert "total_value" in meta_result
    assert "demographics" in meta_result
    assert "snapshot" in meta_result
    assert meta_result["ig_business_account_id"] == params["ig_business_account_id"]
