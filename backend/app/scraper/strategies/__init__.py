from app.scraper.strategies.html import HTMLStrategy
from app.scraper.strategies.json import JSONStrategy
from app.scraper.strategies.shopify_api import ShopifyAPIStrategy
from app.scraper.strategies.size_guide import SizeGuideHTMLStrategy

__all__ = [
    "HTMLStrategy",
    "JSONStrategy",
    "ShopifyAPIStrategy",
    "SizeGuideHTMLStrategy",
]
