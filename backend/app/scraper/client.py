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
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
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
        collected: dict[str, ScrapedProduct] = {}
        for strategy in self.product_strategies:
            try:
                products = strategy.scrape(url)
            except Exception as exc:
                logger.warning("Product strategy {} failed: {}", strategy.name, exc)
                continue
            logger.info("Product strategy {} found {} products", strategy.name, len(products))
            for product in products:
                collected.setdefault(product.handle, product)
            if collected and strategy.name == "shopify_api":
                break
        return list(collected.values())
