from loguru import logger

from app.core.config import Settings, get_settings
from app.scraper.strategies import (
    HTMLStrategy,
    JSONStrategy,
    ShopifyAPIStrategy,
    SizeGuideHTMLStrategy,
)
from app.scraper.types import ProductStrategy, ScrapeResult, ScrapedProduct


class ShopifyScraper:
    """Point d'entrée du moteur d'extraction.

    Orchestrateur qui chaîne plusieurs stratégies d'extraction pour couvrir
    la majorité des boutiques Shopify, quelle que soit la structure de leur
    front (thème classique, headless, SPA Next.js...).
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        # Ordre d'essai : l'API Shopify officielle est la source la plus
        # complète, puis le JSON embarqué, puis le HTML pur (repli).
        self.product_strategies: list[ProductStrategy] = [
            ShopifyAPIStrategy(self.settings),
            JSONStrategy(self.settings),
            HTMLStrategy(self.settings),
        ]
        self.size_guide_strategy = SizeGuideHTMLStrategy(self.settings)

    def scrape(self, url: str) -> ScrapeResult:
        products = self._scrape_products(url)
        size_guides = self.size_guide_strategy.scrape(url)
        return ScrapeResult(products=products, size_guides=size_guides)

    def _scrape_products(self, url: str) -> list[ScrapedProduct]:
        # Dictionnaire clé "handle" : déduplication naturelle des produits,
        # la première stratégie gagnante l'emporte sur les suivantes.
        collected: dict[str, ScrapedProduct] = {}
        for strategy in self.product_strategies:
            try:
                products = strategy.scrape(url)
            except Exception as exc:
                # Une stratégie peut échouer (anti-bot, HTML non standard) :
                # on la signale et on tente la suivante.
                logger.warning("Product strategy {} failed: {}", strategy.name, exc)
                continue
            logger.info("Product strategy {} found {} products", strategy.name, len(products))
            for product in products:
                collected.setdefault(product.handle, product)
            # Résultat complet dès que l'API Shopify répond : inutile
            # d'interroger les autres stratégies.
            if collected and strategy.name == "shopify_api":
                break
        return list(collected.values())
