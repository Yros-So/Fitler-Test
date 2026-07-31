import json
from collections.abc import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.config import Settings
from app.scraper.http import HttpFetcher, normalize_shop_url
from app.scraper.parsing import parse_html
from app.scraper.types import ScrapedProduct, ScrapedVariant


class HTMLStrategy:
    """Stratégie de repli 100 % HTML.

    S'applique aux boutiques sans API ni JSON exploitable : on récupère
    d'abord les données produits des balises JSON-LD (schema.org), sinon on
    liste les liens vers les fiches produits du catalogue.
    """

    name = "html"

    def __init__(self, settings: Settings, fetcher: HttpFetcher | None = None) -> None:
        self.settings = settings
        self.fetcher = fetcher or HttpFetcher(settings)

    def scrape(self, base_url: str) -> list[ScrapedProduct]:
        base = normalize_shop_url(base_url)
        with self.fetcher.client() as client:
            response = self.fetcher.get(client, base)
        soup = parse_html(response.text)
        products = self._json_ld_products(soup, base)
        if products:
            return products
        return self._product_links(soup, base)

    def _json_ld_products(self, soup: BeautifulSoup, base_url: str) -> list[ScrapedProduct]:
        # JSON-LD (schema.org/Product) : données structurées pour le SEO,
        # souvent plus riches que le simple HTML visible.
        products: list[ScrapedProduct] = []
        for script in soup.select('script[type="application/ld+json"]'):
            if not script.string:
                continue
            try:
                payload = json.loads(script.string)
            except json.JSONDecodeError:
                continue
            for product in self._iter_json_ld_products(payload):
                url = str(product.get("url") or base_url)
                # Le dernier segment de l'URL = identifiant (handle) produit.
                handle = url.rstrip("/").split("/")[-1] or str(product.get("sku") or "product")
                image = product.get("image")
                images = image if isinstance(image, list) else ([image] if image else [])
                # "offers" peut être un objet unique ou une liste (prix/stock).
                offers = product.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                products.append(
                    ScrapedProduct(
                        external_id=str(product.get("sku")) if product.get("sku") else None,
                        name=str(product.get("name") or handle),
                        price=offers.get("price") if isinstance(offers, dict) else None,
                        description=product.get("description"),
                        image_urls=[str(item) for item in images if item],
                        vendor=self._brand_name(product.get("brand")),
                        tags=[],
                        handle=handle,
                        url=urljoin(base_url, url),
                        options={},
                        variants=[
                            ScrapedVariant(
                                external_id=str(product.get("sku")) if product.get("sku") else None,
                                title="Default",
                                sku=product.get("sku"),
                                price=offers.get("price") if isinstance(offers, dict) else None,
                                available=self._availability(offers),
                                options={},
                            )
                        ],
                    )
                )
        return products

    def _product_links(self, soup: BeautifulSoup, base_url: str) -> list[ScrapedProduct]:
        # Dernier recours : parcourir les ancres "/products/..." de la page
        # d'accueil pour référencer les fiches produits sans les détailler.
        seen: set[str] = set()
        products: list[ScrapedProduct] = []
        for anchor in soup.select('a[href*="/products/"]'):
            href = anchor.get("href")
            if not href:
                continue
            url = urljoin(base_url, href.split("?")[0]).rstrip("/")
            if url in seen:
                continue
            seen.add(url)
            handle = url.split("/")[-1]
            name = anchor.get_text(" ", strip=True) or handle.replace("-", " ").title()
            products.append(
                ScrapedProduct(
                    external_id=None,
                    name=name,
                    price=None,
                    description=None,
                    image_urls=[],
                    vendor=None,
                    tags=[],
                    handle=handle,
                    url=url,
                    options={},
                    variants=[],
                )
            )
        return products

    def _iter_json_ld_products(self, payload: dict | list) -> Iterable[dict]:
        # Traverse le graphe JSON-LD (@graph) et ne retient que les nœuds
        # typés "Product".
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                yield from self._iter_json_ld_products(graph)
            item_type = item.get("@type")
            if item_type == "Product" or (
                isinstance(item_type, list) and "Product" in item_type
            ):
                yield item

    @staticmethod
    def _brand_name(brand: object) -> str | None:
        # La marque peut être un objet {"name": ...} ou une simple chaîne.
        if isinstance(brand, dict):
            return brand.get("name")
        return str(brand) if brand else None

    @staticmethod
    def _availability(offers: object) -> bool:
        # "availability": "https://schema.org/InStock" => disponible.
        if not isinstance(offers, dict):
            return False
        availability = str(offers.get("availability") or "").lower()
        return "instock" in availability or "in stock" in availability
