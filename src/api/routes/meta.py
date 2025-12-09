# src/api/routes/meta.py

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.routes.auth import get_current_user
from src.schemas.user import UserRead
from src.services.meta_client import MetaClient
from src.utils.logger import get_logger

from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional

import requests


logger = get_logger(__name__)

router = APIRouter(prefix="/meta", tags=["meta"])

meta_client = MetaClient()


@router.get("/instagram/insights")
def get_instagram_insights(
    ig_business_account_id: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
    current_user: UserRead = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Consulta insights básicos da conta Instagram Business.
    """
    try:
        result = meta_client.get_ig_insights(
            ig_business_account_id=ig_business_account_id,
            since=since,
            until=until,
        )
        return {
            "message": "Consulta de insights concluída com sucesso.",
            "meta_result": result,
            "user": current_user.username,
        }
    except RuntimeError as e:
        logger.exception("[Meta] Erro ao buscar insights (RuntimeError)")
        # Erro de configuração ou retorno da Meta
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("[Meta] Erro inesperado ao buscar insights")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ---------- SCHEMAS ----------


class InstagramPublishPayload(BaseModel):
    ig_user_id: str
    image_url: str
    caption: str = ""
    project_id: Optional[int] = None


class InstagramInsightsPayload(BaseModel):
    ig_business_account_id: str
    since: Optional[str] = None
    until: Optional[str] = None


# ---------- ENDPOINT: PUBLICAR IMAGEM ----------


@router.post("/instagram/publish-image")
def publish_instagram_image(
    payload: InstagramPublishPayload,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Publica uma imagem no feed do Instagram via IG_USER_ID.
    """
    try:
        result = meta_client.publish_image(
            ig_user_id=payload.ig_user_id,
            image_url=payload.image_url,
            caption=payload.caption,
            project_id=payload.project_id,
            username=current_user.username,
        )
    except Exception as e:
        logger.exception("Falha ao publicar no Instagram")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Falha ao publicar no Instagram",
                "meta_result": getattr(e, "detail", str(e)),
            },
        )

    return {
        "message": "Publicação realizada com sucesso no Instagram.",
        "meta_result": result,
        "user": current_user.username,
        "project_id": payload.project_id,
    }


# ---------- ENDPOINT: INSIGHTS ----------
@router.get("/instagram/insights")
def get_instagram_insights(
    ig_business_account_id: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
    current_user: UserRead = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Consulta insights básicos da conta Instagram Business.
    """
    try:
        # usa o mesmo método que você já validou no teste de publicação
        result = meta_client.get_ig_insights(
            ig_business_account_id=ig_business_account_id,
            since=since,
            until=until,
        )
        return {
            "message": "Consulta de insights concluída com sucesso.",
            "meta_result": result,
            "user": current_user.username,
        }
    except Exception as e:
        logger.exception("[Meta] Erro ao buscar insights")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
