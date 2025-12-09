# src/services/analyses.py
from typing import List, Optional

from sqlmodel import Session, select

from src.models.analysis import AnalysisHistory


def create_analysis(
    session: Session,
    owner_id: int,
    project_id: Optional[int],
    topic: str,
    platform: str,
    mode: str,
    users_json: str,
    result_json: str,
) -> AnalysisHistory:
    analysis = AnalysisHistory(
        owner_id=owner_id,
        project_id=project_id,
        topic=topic,
        platform=platform,
        mode=mode,
        users_json=users_json,
        result_json=result_json,
    )
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    return analysis


def list_analyses(
    session: Session,
    owner_id: int,
    limit: int = 50,
    project_id: Optional[int] = None,
) -> List[AnalysisHistory]:
    stmt = select(AnalysisHistory).where(AnalysisHistory.owner_id == owner_id)

    if project_id is not None:
        stmt = stmt.where(AnalysisHistory.project_id == project_id)

    stmt = stmt.order_by(AnalysisHistory.id.desc()).limit(limit)

    return list(session.exec(stmt))


def get_analysis_by_id(
    session: Session,
    owner_id: int,
    analysis_id: int,
) -> Optional[AnalysisHistory]:
    stmt = select(AnalysisHistory).where(
        AnalysisHistory.id == analysis_id,
        AnalysisHistory.owner_id == owner_id,
    )
    return session.exec(stmt).first()
