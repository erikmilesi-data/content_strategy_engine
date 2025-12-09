# src/api/routes/content_strategy.py

from typing import List, Optional

import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.suggestion_engine.suggestion_core import (
    get_basic_suggestions,
    get_platform_suggestions,
)
from src.audience_analyzer.audience_core import analyze_audience, profile_audience
from src.posting_time_optimizer.time_core import suggest_best_times
from src.utils.logger import get_logger
from src.api.routes.auth import get_current_user
from src.schemas.user import UserRead
from src.database.sqlmodel_db import get_session
from src.services.analyses import (
    create_analysis,
    list_analyses,
    get_analysis_by_id,
)
from src.services.projects import get_project

logger = get_logger(__name__)

router = APIRouter(prefix="/content", tags=["content_strategy"])


class AudienceUser(BaseModel):
    age: int
    gender: str
    region: str


class ContentStrategyRequest(BaseModel):
    topic: str
    platform: str
    mode: str = "rich"
    users: Optional[List[AudienceUser]] = None
    project_id: Optional[int] = None


@router.post("/strategy")
def generate_content_strategy(
    payload: ContentStrategyRequest,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Gera uma estratégia de conteúdo, salva no histórico (SQLModel)
    e retorna o resultado completo.
    """
    logger.info(
        f"[user={current_user.username}] Gerando estratégia para "
        f"topic={payload.topic}, platform={payload.platform}, "
        f"users={len(payload.users or [])}, project_id={payload.project_id}"
    )

    users_dicts = [u.model_dump() for u in (payload.users or [])]

    audience_summary = analyze_audience(users_dicts)
    audience_profiles = profile_audience(users_dicts)

    dominant_profile = audience_profiles[0] if audience_profiles else None
    dominant_age_bucket = dominant_profile["age_bucket"] if dominant_profile else None
    dominant_region = (
        max(audience_summary["by_region"], key=audience_summary["by_region"].get)
        if audience_summary.get("by_region")
        else None
    )

    if payload.mode == "basic":
        suggestions = get_basic_suggestions(payload.topic)
    else:
        suggestions = get_platform_suggestions(payload.topic, payload.platform)

    time_slots = suggest_best_times(
        platform=payload.platform,
        main_age_bucket=dominant_age_bucket,
        region_main=dominant_region,
    )

    final_response = {
        "topic": payload.topic,
        "platform": payload.platform,
        "mode": payload.mode,
        "audience": {
            "summary": audience_summary,
            "profiles": audience_profiles,
            "dominant_profile": dominant_profile,
        },
        "suggestions": suggestions,
        "best_times": time_slots,
        "project_id": payload.project_id,
    }

    # Salvar no histórico (SQLModel)
    analysis = create_analysis(
        session=session,
        owner_id=current_user.id,
        project_id=payload.project_id,
        topic=payload.topic,
        platform=payload.platform,
        mode=payload.mode,
        users_json=json.dumps(users_dicts, ensure_ascii=False),
        result_json=json.dumps(final_response, ensure_ascii=False),
    )

    # Retornamos o mesmo final_response (sem depender do objeto salvo)
    return final_response


@router.get("/history")
def get_history(
    limit: int = 50,
    project_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Retorna o histórico SOMENTE do usuário logado.
    Opcionalmente, pode ser filtrado por projeto.
    Agora usando SQLModel.
    """
    analyses = list_analyses(
        session=session,
        owner_id=current_user.id,
        limit=limit,
        project_id=project_id,
    )

    history = []
    for a in analyses:
        project_name = None
        if a.project_id:
            project = get_project(
                session, owner_id=current_user.id, project_id=a.project_id
            )
            if project:
                project_name = project.name

        history.append(
            {
                "id": a.id,
                "timestamp": a.created_at.isoformat(),
                "topic": a.topic,
                "platform": a.platform,
                "mode": a.mode,
                "project_id": a.project_id,
                "project_name": project_name,
            }
        )

    return {"history": history}


@router.get("/history/{entry_id}")
def get_history_entry(
    entry_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Retorna uma entrada específica do histórico,
    garantindo que pertence ao usuário logado.
    """
    analysis = get_analysis_by_id(
        session=session,
        owner_id=current_user.id,
        analysis_id=entry_id,
    )

    if not analysis:
        return {"error": "Entry not found"}

    return {
        "id": analysis.id,
        "timestamp": analysis.created_at.isoformat(),
        "topic": analysis.topic,
        "platform": analysis.platform,
        "mode": analysis.mode,
        "project_id": analysis.project_id,
        "users": json.loads(analysis.users_json),
        "result": json.loads(analysis.result_json),
    }
