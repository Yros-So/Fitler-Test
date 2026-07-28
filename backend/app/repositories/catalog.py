from decimal import Decimal, InvalidOperation

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, ProductVariant
from app.models.size_guide import SizeGuide
from app.scraper.types import ScrapeResult, ScrapedProduct, ScrapedSizeGuide


def _decimal_or_none(value: str | int | float | Decimal | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


class CatalogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_products(
        self,
        *,
        search: str | None = None,
        page: int = 1,
        page_size: int = 25,
        sort: str = "name",
    ) -> tuple[list[Product], int]:
        statement = select(Product).options(selectinload(Product.variants))
        count_statement = select(func.count(Product.id))

        if search:
            pattern = f"%{search}%"
            criteria = or_(
                Product.name.ilike(pattern),
                Product.vendor.ilike(pattern),
                Product.handle.ilike(pattern),
            )
            statement = statement.where(criteria)
            count_statement = count_statement.where(criteria)

        sort_column = {
            "name": Product.name,
            "price": Product.price,
            "created_at": Product.created_at,
        }.get(sort, Product.name)

        total = self.session.scalar(count_statement) or 0
        items = self.session.scalars(
            statement.order_by(sort_column).offset((page - 1) * page_size).limit(page_size)
        ).all()
        return list(items), total

    def get_product(self, product_id: str) -> Product | None:
        return self.session.scalar(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.variants), selectinload(Product.size_guides))
        )

    def list_size_guides(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[list[SizeGuide], int]:
        total = self.session.scalar(select(func.count(SizeGuide.id))) or 0
        items = self.session.scalars(
            select(SizeGuide)
            .order_by(SizeGuide.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(items), total

    def persist_result(self, website_id: str, result: ScrapeResult) -> dict:
        products_written = 0
        variants_written = 0
        guides_written = 0

        for scraped in result.products:
            product = self._upsert_product(website_id, scraped)
            products_written += 1
            variants_written += len(scraped.variants)
            self.session.execute(delete(ProductVariant).where(ProductVariant.product_id == product.id))
            for variant in scraped.variants:
                self.session.add(
                    ProductVariant(
                        product_id=product.id,
                        external_id=variant.external_id,
                        title=variant.title,
                        sku=variant.sku,
                        price=_decimal_or_none(variant.price),
                        available=variant.available,
                        options=variant.options,
                    )
                )

        self.session.execute(delete(SizeGuide).where(SizeGuide.website_id == website_id))
        for guide in result.size_guides:
            self.session.add(self._build_size_guide(website_id, guide))
            guides_written += 1

        self.session.flush()
        return {
            "products": products_written,
            "variants": variants_written,
            "size_guides": guides_written,
        }

    def _upsert_product(self, website_id: str, scraped: ScrapedProduct) -> Product:
        product = self.session.scalar(
            select(Product).where(
                Product.website_id == website_id,
                Product.handle == scraped.handle,
            )
        )
        if product is None:
            product = Product(
                website_id=website_id,
                handle=scraped.handle,
                name=scraped.name,
                url=scraped.url,
            )
            self.session.add(product)

        product.external_id = scraped.external_id
        product.name = scraped.name
        product.price = _decimal_or_none(scraped.price)
        product.description = scraped.description
        product.image_urls = scraped.image_urls
        product.vendor = scraped.vendor
        product.tags = scraped.tags
        product.url = scraped.url
        product.options = scraped.options
        self.session.flush()
        return product

    def _build_size_guide(self, website_id: str, guide: ScrapedSizeGuide) -> SizeGuide:
        return SizeGuide(
            website_id=website_id,
            product_id=None,
            title=guide.title,
            source_url=guide.source_url,
            content={
                "tables": guide.tables,
                "source_type": guide.source_type,
                "metadata": guide.metadata,
            },
            raw_text=guide.text,
        )
