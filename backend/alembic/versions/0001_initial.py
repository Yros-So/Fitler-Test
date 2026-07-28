"""Initial schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "websites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_websites_domain"), "websites", ["domain"], unique=False)
    op.create_index(op.f("ix_websites_url"), "websites", ["url"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("website_id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_urls", sa.JSON(), nullable=False),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("handle", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("website_id", "handle", name="uq_products_website_handle"),
    )
    op.create_index(op.f("ix_products_external_id"), "products", ["external_id"], unique=False)
    op.create_index(op.f("ix_products_handle"), "products", ["handle"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_vendor"), "products", ["vendor"], unique=False)
    op.create_index(op.f("ix_products_website_id"), "products", ["website_id"], unique=False)

    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("website_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stats", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scrape_jobs_status"), "scrape_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_scrape_jobs_website_id"), "scrape_jobs", ["website_id"], unique=False)

    op.create_table(
        "size_guides",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("website_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["website_id"], ["websites.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_size_guides_product_id"), "size_guides", ["product_id"], unique=False)
    op.create_index(op.f("ix_size_guides_title"), "size_guides", ["title"], unique=False)
    op.create_index(op.f("ix_size_guides_website_id"), "size_guides", ["website_id"], unique=False)

    op.create_table(
        "variants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("sku", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_variants_external_id"), "variants", ["external_id"], unique=False)
    op.create_index(op.f("ix_variants_product_id"), "variants", ["product_id"], unique=False)
    op.create_index(op.f("ix_variants_sku"), "variants", ["sku"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_variants_sku"), table_name="variants")
    op.drop_index(op.f("ix_variants_product_id"), table_name="variants")
    op.drop_index(op.f("ix_variants_external_id"), table_name="variants")
    op.drop_table("variants")
    op.drop_index(op.f("ix_size_guides_website_id"), table_name="size_guides")
    op.drop_index(op.f("ix_size_guides_title"), table_name="size_guides")
    op.drop_index(op.f("ix_size_guides_product_id"), table_name="size_guides")
    op.drop_table("size_guides")
    op.drop_index(op.f("ix_scrape_jobs_website_id"), table_name="scrape_jobs")
    op.drop_index(op.f("ix_scrape_jobs_status"), table_name="scrape_jobs")
    op.drop_table("scrape_jobs")
    op.drop_index(op.f("ix_products_website_id"), table_name="products")
    op.drop_index(op.f("ix_products_vendor"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_handle"), table_name="products")
    op.drop_index(op.f("ix_products_external_id"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_websites_url"), table_name="websites")
    op.drop_index(op.f("ix_websites_domain"), table_name="websites")
    op.drop_table("websites")
