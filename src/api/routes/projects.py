# src/api/routes/projects.py
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.database.sqlmodel_db import get_session
from src.schemas.project import ProjectCreate, ProjectRead
from src.schemas.user import UserRead
from src.services.projects import (
    create_project as service_create_project,
    list_projects,
)
from src.api.routes.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectRead])
def get_my_projects(
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    # current_user agora é um UserRead (com .id), não dict
    return list_projects(session, owner_id=current_user.id)


@router.post("/", response_model=ProjectRead)
def create_project_endpoint(
    payload: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return service_create_project(session, owner_id=current_user.id, data=payload)
