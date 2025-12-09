# src/models/project.py
from __future__ import annotations

from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class Project(SQLModel, table=True):
    """
    Projeto / Campanha de marketing do usuário.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # dono do projeto = id do usuário da tabela de auth
    owner_id: int = Field(index=True)

    name: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

    # novo: IG User ID associado a esse projeto (opcional)
    ig_user_id: Optional[str] = Field(default=None, max_length=64)

    created_at: datetime = Field(default_factory=datetime.utcnow)
