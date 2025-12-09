# src/database/sqlmodel_db.py

from typing import Generator

from sqlmodel import SQLModel, create_engine, Session

from src.models.project import Project  # garante que a tabela exista
from src.models.analysis import AnalysisHistory  # nosso novo modelo


# 👉 Banco específico para os recursos que usarem SQLModel (ex: projetos/análises)
DATABASE_URL = "sqlite:///./content_strategy_sqlmodel.db"

# Para SQLite, geralmente é bom habilitar check_same_thread=False
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependência para injeção de sessão do SQLModel (FastAPI Depends).
    """
    with Session(engine) as session:
        yield session


def init_db_sqlmodel() -> None:
    """
    Inicializa as tabelas do SQLModel.
    """
    SQLModel.metadata.create_all(engine)
