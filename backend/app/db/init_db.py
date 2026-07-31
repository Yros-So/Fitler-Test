from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    # Importe les modèles pour que SQLAlchemy les enregistre sur Base,
    # puis crée les tables manquantes (équivalent d'un migrate léger).
    import app.models.product  # noqa: F401
    import app.models.scrape_job  # noqa: F401
    import app.models.size_guide  # noqa: F401
    import app.models.website  # noqa: F401

    Base.metadata.create_all(bind=engine)
