# src/models/analysis.py
from __future__ import annotations

from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class AnalysisHistory(SQLModel, table=True):
    """
    Histórico de análises de conteúdo, por usuário e (opcionalmente) por projeto.
    Fica no banco SQLModel (content_strategy_sqlmodel.db).
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Usuário dono da análise (mesmo user_id do JWT)
    owner_id: int = Field(index=True)

    # Projeto ao qual a análise pertence (pode ser None, para compatibilidade)
    project_id: Optional[int] = Field(default=None, index=True)

    topic: str
    platform: str
    mode: str

    users_json: str
    result_json: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
