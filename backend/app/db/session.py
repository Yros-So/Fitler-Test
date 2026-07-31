from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _resolve_db_url(url: str) -> str:
    # PostgreSQL : on force le driver psycopg3 (recommandé par SQLAlchemy
    # 2.x) ; SQLite reste inchangé.
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


_db_url = _resolve_db_url(settings.database_url)

# Options de connexion : SQLite est mono-thread par défaut (d'où
# check_same_thread=False) ; PostgreSQL exige un SSL pour la connexion.
if _db_url.startswith("sqlite"):
    connect_args: dict = {"check_same_thread": False}
else:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    _db_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # vérifie la connexion avant usage (bases externes)
    pool_size=5,
    max_overflow=10,
)
# Fabrique de sessions : chaque requête / job ouvre sa propre session.
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    # Dépendance FastAPI : fournit une session par requête et garantit
    # sa fermeture même en cas d'erreur.
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
