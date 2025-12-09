# src/services/projects.py
from typing import List, Optional

from sqlmodel import Session, select

from src.models.project import Project
from src.schemas.project import ProjectCreate


def create_project(session: Session, owner_id: int, data: ProjectCreate) -> Project:
    project = Project(
        owner_id=owner_id,
        name=data.name,
        description=data.description,
        ig_user_id=data.ig_user_id,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session, owner_id: int) -> List[Project]:
    stmt = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(Project.created_at.desc())
    )
    return list(session.exec(stmt))


def get_project(session: Session, owner_id: int, project_id: int) -> Project | None:
    return session.get(Project, project_id) if project_id else None
