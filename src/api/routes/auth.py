# src/api/routes/auth.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.database.db import get_user_by_username
from src.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
)
from src.schemas.auth import LoginPayload, Token
from src.schemas.user import UserRead
from src.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# esquema padrão de Bearer para o FastAPI gerar o Authorize
bearer_scheme = HTTPBearer(auto_error=True)


@router.post("/login", response_model=Token)
def login(payload: LoginPayload):
    """
    Faz login com username/senha e devolve um JWT.
    """
    row = get_user_by_username(payload.username)

    if not row or not verify_password(payload.password, row["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    user = UserRead(id=row["id"], username=row["username"])

    access_token = create_access_token(
        {
            "sub": user.username,
            "user_id": user.id,
            "iat": datetime.utcnow().timestamp(),
        }
    )

    logger.info(f"Login bem-sucedido para usuário '{user.username}'")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserRead:
    """
    Extrai o usuário atual a partir do token Bearer.
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    username = payload.get("sub")
    user_id = payload.get("user_id")

    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    return UserRead(id=user_id, username=username)
