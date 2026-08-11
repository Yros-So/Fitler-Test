from decimal import Decimal, InvalidOperation

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product, ProductVariant
from app.models.size_guide import SizeGuide
from app.scraper.strategies.size_guide import is_guide_page
from app.scraper.types import ScrapeResult, ScrapedProduct, ScrapedSizeGuide


def _decimal_or_none(value: str | int | float | Decimal | None) -> Decimal | None:
    # Conversion sûre en Decimal pour les colonnes Numeric (prix) :
    # toute valeur non convertible devient NULL.
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


class CatalogRepository:
    """Accès en lecture/écriture au catalogue produits et guides de taille."""

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
        # Requête paginée + recherche insensible à la casse + tri.
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

        # Tri sécurisé : colonne choisie depuis un dictionnaire fermé
        # (jamais une valeur arbitraire de l'utilisateur).
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
        # Fiche produit détaillée : variantes + guides associés chargés.
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
        # Seuls les guides réellement utilisables sont exposés : ceux qui
        # ont des tableaux de mesures, ou une page explicitement dédiée aux
        # tailles. Les faux positifs (produits, collections, FAQ, entretien)
        # sont masqués sans être supprimés en base.
        guides = self.session.scalars(
            select(SizeGuide).order_by(SizeGuide.created_at.desc())
        ).all()
        visible = [guide for guide in guides if self._is_visible_guide(guide)]
        total = len(visible)
        start = (page - 1) * page_size
        return visible[start : start + page_size], total

    @staticmethod
    def _is_visible_guide(guide: SizeGuide) -> bool:
        # Les PDF (fichiers) ne sont pas des guides exploitables ici.
        if (guide.source_url or "").lower().endswith(".pdf"):
            return False
        table_count = (guide.content or {}).get("metadata", {}).get("table_count", 0)
        if table_count >= 1:
            return True
        return is_guide_page(guide.title or "", guide.source_url or "")

    def persist_result(self, website_id: str, result: ScrapeResult) -> dict:
        """Écrit le résultat d'un scraping en base (remplace les données
        existantes de la boutique par les plus récentes)."""
        products_written = 0
        variants_written = 0
        guides_written = 0

        for scraped in result.products:
            # Upsert par (website_id, handle) : met à jour ou crée le produit.
            product = self._upsert_product(website_id, scraped)
            products_written += 1
            variants_written += len(scraped.variants)
            # Variantes recréées à chaque run (source de vérité = scraping).
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

        # Guides de taille remplacés eux aussi pour refléter le dernier scan.
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
            # Nouveau produit : on initialise l'identifiant métier (handle).
            product = Product(
                website_id=website_id,
                handle=scraped.handle,
                name=scraped.name,
                url=scraped.url,
            )
            self.session.add(product)

        # Mise à jour de toutes les données extraites.
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
        # Les tableaux et métadonnées du guide sont stockés en JSON.
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
