# frontend/api_client.py

import requests
import json
from typing import Dict, Any, Optional, List


class APIClient:
    def __init__(self, base_url: str):
        # Ex: "http://127.0.0.1:8000/api"
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None

    # -----------------------------------
    # Helpers internos
    # -----------------------------------
    def _headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # -----------------------------------
    # Auth
    # -----------------------------------
    def login(self, username: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}

        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Login falhou ({resp.status_code}): {resp.text}")

        data = resp.json()
        self.token = data["access_token"]
        return data

    def register(self, username: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/register"
        payload = {"username": username, "password": password}

        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Registro falhou ({resp.status_code}): {resp.text}")

        return resp.json()

    # -----------------------------------
    # Estratégia de conteúdo
    # -----------------------------------
    def generate_strategy(
        self,
        topic: str,
        platform: str,
        mode: str,
        users: Optional[List[Dict[str, Any]]] = None,
        project_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/content/strategy"
        payload = {
            "topic": topic,
            "platform": platform,
            "mode": mode,
            "users": users or [],
            "project_id": project_id,
        }

        resp = requests.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=20,
        )

        if resp.status_code == 401:
            # deixa o frontend saber que o token está inválido/expirado
            raise PermissionError("Não autorizado (401). Token inválido ou expirado.")

        if resp.status_code != 200:
            raise Exception(
                f"Erro ao gerar estratégia ({resp.status_code}): {resp.text}"
            )

        return resp.json()

    def get_history(
        self, limit: int = 50, project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/content/history"
        params = {"limit": limit}
        if project_id is not None:
            params["project_id"] = project_id

        resp = requests.get(
            url,
            params=params,
            headers=self._headers(),
            timeout=10,
        )

        if resp.status_code == 401:
            raise PermissionError("Não autorizado (401) ao buscar histórico.")

        if resp.status_code != 200:
            raise Exception(
                f"Erro ao buscar histórico ({resp.status_code}): {resp.text}"
            )

        return resp.json()

    def get_history_entry(self, entry_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/content/history/{entry_id}"

        resp = requests.get(
            url,
            headers=self._headers(),
            timeout=10,
        )

        if resp.status_code == 401:
            raise PermissionError("Não autorizado (401) ao carregar entrada.")

        if resp.status_code != 200:
            raise Exception(
                f"Erro ao carregar entrada ({resp.status_code}): {resp.text}"
            )

        return resp.json()

    # -----------------------------------
    # Projetos
    # -----------------------------------
    def list_projects(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/projects/"
        resp = requests.get(url, headers=self._headers(), timeout=10)

        if resp.status_code == 401:
            raise PermissionError("Não autorizado (401) ao listar projetos.")
        if resp.status_code != 200:
            raise Exception(
                f"Erro ao listar projetos ({resp.status_code}): {resp.text}"
            )

        return resp.json()

    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        ig_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/projects/"
        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "ig_user_id": ig_user_id,
        }

        resp = requests.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=10,
        )

        if resp.status_code == 401:
            raise PermissionError("Não autorizado (401) ao criar projeto.")
        if resp.status_code != 200:
            raise Exception(f"Erro ao criar projeto ({resp.status_code}): {resp.text}")

        return resp.json()

    # -----------------------------------
    # Instagram Insights (Meta)
    # -----------------------------------

    def get_ig_insights(
        self,
        ig_business_account_id: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chama o endpoint GET /meta/instagram/insights do backend,
        passando os parâmetros via query string.
        """
        url = f"{self.base_url}/meta/instagram/insights"

        params = {"ig_business_account_id": ig_business_account_id}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        resp = requests.get(
            url,
            params=params,
            headers=self._headers(),
            timeout=30,
        )

        if resp.status_code == 401:
            raise PermissionError(
                "Não autorizado (401) ao buscar insights do Instagram."
            )

        if resp.status_code != 200:
            raise Exception(
                f"Erro ao buscar insights ({resp.status_code}): {resp.text}"
            )

        return resp.json()
