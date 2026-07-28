from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("website_id", "handle", name="uq_products_website_handle"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    website_id: Mapped[str] = mapped_column(ForeignKey("websites.id"), index=True)
    external_id: Mapped[str | None] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(512), index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    description: Mapped[str | None] = mapped_column(Text)
    image_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    vendor: Mapped[str | None] = mapped_column(String(255), index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    handle: Mapped[str] = mapped_column(String(512), index=True)
    url: Mapped[str] = mapped_column(String(2048))
    options: Mapped[dict] = mapped_column(JSON, default=dict)

    website: Mapped["Website"] = relationship(back_populates="products")  # noqa: F821
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    size_guides: Mapped[list["SizeGuide"]] = relationship(back_populates="product")  # noqa: F821


class ProductVariant(TimestampMixin, Base):
    __tablename__ = "variants"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    external_id: Mapped[str | None] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(512))
    sku: Mapped[str | None] = mapped_column(String(255), index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    options: Mapped[dict] = mapped_column(JSON, default=dict)

    product: Mapped["Product"] = relationship(back_populates="variants")  # noqa: F821
