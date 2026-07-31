from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Website(TimestampMixin, Base):
    """Boutique en ligne scrapée (URL canonique unique)."""

    __tablename__ = "websites"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="website",
        cascade="all, delete-orphan",
    )
    size_guides: Mapped[list["SizeGuide"]] = relationship(  # noqa: F821
        back_populates="website",
        cascade="all, delete-orphan",
    )
    scrape_jobs: Mapped[list["ScrapeJob"]] = relationship(  # noqa: F821
        back_populates="website",
        cascade="all, delete-orphan",
    )
