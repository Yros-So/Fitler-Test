from uuid import uuid4

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SizeGuide(TimestampMixin, Base):
    __tablename__ = "size_guides"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    website_id: Mapped[str] = mapped_column(ForeignKey("websites.id"), index=True)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"), index=True)
    title: Mapped[str] = mapped_column(String(512), index=True)
    source_url: Mapped[str] = mapped_column(String(2048))
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_text: Mapped[str | None] = mapped_column(Text)

    website: Mapped["Website"] = relationship(back_populates="size_guides")  # noqa: F821
    product: Mapped["Product | None"] = relationship(back_populates="size_guides")  # noqa: F821
