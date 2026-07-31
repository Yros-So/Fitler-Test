from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.db.session import get_session

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Code exécuté au démarrage de l'application : config des logs puis
    # création automatique des tables si activé (utile en local/démo).
    configure_logging()
    if settings.auto_create_tables:
        init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS : autorise le frontend (localhost en dev, workers.dev en prod)
# à appeler l'API depuis le navigateur.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/ready")
def ready(session: Session = Depends(get_session)):
    # Endpoint de readiness : vérifie que la base de données répond
    # (utilisé par Render pour les healthchecks).
    try:
        session.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "not_ready",
            "database": "disconnected",
        }
