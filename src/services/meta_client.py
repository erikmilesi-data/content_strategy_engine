# src/services/meta_client.py

import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime, date

from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetaClient:
    # Se quiser, podemos manter também a constante de classe:
    BASE_URL = "https://graph.facebook.com/v24.0"

    def __init__(self, access_token: Optional[str] = None):
        # tanto faz usar self.base_url ou self.BASE_URL; vou deixar ambos coerentes
        self.base_url = self.BASE_URL
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN")

    def _ensure_token(self) -> Optional[Dict[str, Any]]:
        """
        Verifica se há token configurado. Se não houver, retorna um dict de erro
        padronizado; caso contrário, None.
        """
        if not self.access_token:
            return {
                "status": "error",
                "detail": "META_ACCESS_TOKEN não configurado no servidor.",
            }
        return None

    # -----------------------------------------------------------
    # MÉTODO AUXILIAR: Verifica o token (para fluxos que não querem
    # devolver dict de erro, mas lançar exceção)
    # -----------------------------------------------------------
    def _check_token(self):
        if not self.access_token:
            logger.warning("[MetaClient] META_ACCESS_TOKEN não configurado.")
            raise RuntimeError("META_ACCESS_TOKEN não configurado no servidor.")

    # -----------------------------------------------------------
    # NORMALIZAÇÃO DE DATA (aceita str, date, datetime)
    # (hoje não está sendo usada, mas deixei pronta)
    # -----------------------------------------------------------
    def _normalize_date(self, value: Optional[Any]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        return str(value)

    # -----------------------------------------------------------
    # PUBLICAR IMAGEM NO INSTAGRAM
    # -----------------------------------------------------------
    def publish_image(
        self,
        ig_user_id: str,
        image_url: str,
        caption: str = "",
    ) -> Dict[str, Any]:
        """
        Publica uma imagem no feed do Instagram (Business/Creator)
        """
        self._check_token()

        # 1) Criar container
        container_url = f"{self.base_url}/{ig_user_id}/media"
        params_container = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }

        r1 = requests.post(container_url, data=params_container, timeout=30)
        try:
            data1 = r1.json()
        except Exception:
            data1 = {"error": "invalid JSON", "raw": r1.text}

        if r1.status_code != 200:
            return {
                "step": "create_media",
                "status_code": r1.status_code,
                "error": data1,
            }

        creation_id = data1.get("id")

        # 2) Publicar
        publish_url = f"{self.base_url}/{ig_user_id}/media_publish"
        params_publish = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }

        r2 = requests.post(publish_url, data=params_publish, timeout=30)
        try:
            data2 = r2.json()
        except Exception:
            data2 = {"error": "invalid JSON", "raw": r2.text}

        if r2.status_code != 200:
            return {
                "step": "publish_media",
                "status_code": r2.status_code,
                "creation_id": creation_id,
                "error": data2,
            }

        return {
            "step": "done",
            "status_code": 200,
            "creation_id": creation_id,
            "publish_result": data2,
        }

    # -----------------------------------------------------------
    # INSIGHTS PARA IG BUSINESS ACCOUNT
    # -----------------------------------------------------------
    def get_ig_insights(
        self,
        ig_business_account_id: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Busca um pacote de métricas da conta Instagram Business:
        - time_series: métricas diárias (ex: reach)
        - total_value: métricas agregadas (ex: likes, comments, etc.)
        - demographics: métricas demográficas (lifetime)
        - snapshot: seguidores, posts, etc.
        """
        token_error = self._ensure_token()
        if token_error:
            return token_error

        # Base de parâmetros para chamadas com janela de tempo
        base_params: Dict[str, Any] = {
            "access_token": self.access_token,
        }
        if since:
            base_params["since"] = since
        if until:
            base_params["until"] = until

        result: Dict[str, Any] = {}

        # -------------------------------------------------
        # 1) MÉTRICAS EM SÉRIE TEMPORAL (period=day)
        #    -> usar apenas métricas que a Meta aceita com period=day
        # -------------------------------------------------
        time_series_metrics = ["reach"]  # aqui dá pra adicionar impressions, etc.

        try:
            params_ts = {
                **base_params,
                "metric": ",".join(time_series_metrics),
                "period": "day",
            }
            resp_ts = requests.get(
                f"{self.base_url}/{ig_business_account_id}/insights",
                params=params_ts,
                timeout=20,
            )
            try:
                body_ts = resp_ts.json()
            except Exception:
                body_ts = resp_ts.text

            result["time_series"] = {
                "status_code": resp_ts.status_code,
                "body": body_ts,
                "step": "time_series",
                "requested_metrics": time_series_metrics,
            }
        except Exception as e:
            result["time_series"] = {
                "status_code": 500,
                "body": str(e),
                "step": "time_series",
                "requested_metrics": time_series_metrics,
            }

        # -------------------------------------------------
        # 2) MÉTRICAS TOTAL_VALUE (agregadas)
        #    -> precisam de metric_type=total_value
        # -------------------------------------------------
        total_value_metrics = [
            "accounts_engaged",
            "total_interactions",
            "likes",
            "comments",
            "shares",
            "saves",
            "replies",
            "website_clicks",
            "profile_links_taps",
            "views",
            "content_views",
            "profile_views",
        ]

        try:
            params_tv = {
                **base_params,
                "metric": ",".join(total_value_metrics),
                "metric_type": "total_value",
                "period": "day",
            }
            resp_tv = requests.get(
                f"{self.base_url}/{ig_business_account_id}/insights",
                params=params_tv,
                timeout=20,
            )
            try:
                body_tv = resp_tv.json()
            except Exception:
                body_tv = resp_tv.text

            result["total_value"] = {
                "status_code": resp_tv.status_code,
                "body": body_tv,
                "step": "total_value",
                "requested_metrics": total_value_metrics,
            }
        except Exception as e:
            result["total_value"] = {
                "status_code": 500,
                "body": str(e),
                "step": "total_value",
                "requested_metrics": total_value_metrics,
            }

        # -------------------------------------------------
        # 3) MÉTRICAS DEMOGRÁFICAS (lifetime + timeframe)
        # -------------------------------------------------
        demo_metrics = [
            "engaged_audience_demographics",
            "reached_audience_demographics",
            "follower_demographics",
        ]

        try:
            # Para demographics, a Meta exige timeframe com um destes valores:
            # last_90_days, this_week, prev_month, this_month,
            # last_30_days, last_14_days
            params_demo = {
                "access_token": self.access_token,
                "metric": ",".join(demo_metrics),
                "period": "lifetime",
                "timeframe": "last_30_days",  # 👈 valor válido segundo a mensagem de erro
            }

            resp_demo = requests.get(
                f"{self.base_url}/{ig_business_account_id}/insights",
                params=params_demo,
                timeout=20,
            )
            try:
                body_demo = resp_demo.json()
            except Exception:
                body_demo = resp_demo.text

            result["demographics"] = {
                "status_code": resp_demo.status_code,
                "body": body_demo,
                "step": "demographics",
                "requested_metrics": demo_metrics,
            }
        except Exception as e:
            result["demographics"] = {
                "status_code": 500,
                "body": str(e),
                "step": "demographics",
                "requested_metrics": demo_metrics,
            }

        # -------------------------------------------------
        # 4) SNAPSHOT (seguidores, posts, etc.)
        # -------------------------------------------------
        try:
            params_snap = {
                "access_token": self.access_token,
                "fields": "followers_count,media_count",
            }
            resp_snap = requests.get(
                f"{self.base_url}/{ig_business_account_id}",
                params=params_snap,
                timeout=20,
            )
            try:
                body_snap = resp_snap.json()
            except Exception:
                body_snap = resp_snap.text

            result["snapshot"] = {
                "status_code": resp_snap.status_code,
                "body": body_snap,
                "step": "snapshot",
            }
        except Exception as e:
            result["snapshot"] = {
                "status_code": 500,
                "body": str(e),
                "step": "snapshot",
            }

        return result

    # -----------------------------------------------------------
    # PUBLICAR IMAGEM NO INSTAGRAM
    # -----------------------------------------------------------
    def publish_image(
        self,
        ig_user_id: str,
        image_url: str,
        caption: str = "",
    ) -> Dict[str, Any]:
        """
        Publica uma imagem no feed do Instagram (Business/Creator).

        Fluxo:
        1) Cria um container de mídia no endpoint:
           POST /{ig_user_id}/media
        2) Publica o container:
           POST /{ig_user_id}/media_publish
        3) Retorna o ID da publicação final

        Retornos detalhados para debug:
        - step: etapa do processo
        - status_code: HTTP status
        - creation_id: id do container criado
        - publish_result: resposta final da publicação
        """
        # Garantir que o token foi configurado
        if not self.access_token:
            return {
                "step": "check_token",
                "status_code": 400,
                "error": "META_ACCESS_TOKEN não configurado no servidor.",
            }

        # 1) Criar container de mídia
        container_url = f"{self.base_url}/{ig_user_id}/media"

        params_container = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }

        r1 = requests.post(container_url, data=params_container, timeout=30)
        try:
            data1 = r1.json()
        except Exception:
            data1 = {"raw": r1.text, "error": "Invalid JSON in response"}

        if r1.status_code != 200:
            return {
                "step": "create_media",
                "status_code": r1.status_code,
                "error": data1,
            }

        creation_id = data1.get("id")

        # 2) Publicar container
        publish_url = f"{self.base_url}/{ig_user_id}/media_publish"

        params_publish = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }

        r2 = requests.post(publish_url, data=params_publish, timeout=30)
        try:
            data2 = r2.json()
        except Exception:
            data2 = {"raw": r2.text, "error": "Invalid JSON in response"}

        if r2.status_code != 200:
            return {
                "step": "publish_media",
                "status_code": r2.status_code,
                "creation_id": creation_id,
                "error": data2,
            }

        # Retorno final
        return {
            "step": "done",
            "status_code": 200,
            "creation_id": creation_id,
            "publish_result": data2,
        }
