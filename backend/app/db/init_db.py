from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    import app.models.product  # noqa: F401
    import app.models.scrape_job  # noqa: F401
    import app.models.size_guide  # noqa: F401
    import app.models.website  # noqa: F401

    Base.metadata.create_all(bind=engine)
