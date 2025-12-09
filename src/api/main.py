# src/api/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.api.routes.auth import router as auth_router
from src.api.routes.users import router as users_router
from src.api.routes.content_strategy import router as content_strategy_router
from src.api.routes.projects import router as projects_router
from src.database.sqlmodel_db import init_db_sqlmodel
from src.database.db import init_db as init_history_db

from src.api.routes.meta import router as meta_router


from src.api.routes.meta import router as meta_router

app = FastAPI(
    title="StratifyAI API",
    version="0.1.0",
    description="Backend da StratifyAI",
)


# ---------- Routers ----------
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(content_strategy_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(meta_router, prefix="/api")
app.include_router(meta_router, prefix="/api")


# ---------- Healthcheck ----------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- OpenAPI com bearer global ----------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"OAuth2PasswordBearer": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ---------- Startup ----------
@app.on_event("startup")
def on_startup():
    # DB de usuários/projetos (SQLModel)
    init_db_sqlmodel()
    # DB de histórico (sqlite simples)
    init_history_db()
