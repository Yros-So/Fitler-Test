from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _resolve_db_url(url: str) -> str:
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1).replace("postgres://", "postgresql+psycopg://", 1)
    return url


_db_url = _resolve_db_url(settings.database_url)

connect_args = {"check_same_thread": False} if _db_url.startswith("sqlite") else {}

engine = create_engine(
    _db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
