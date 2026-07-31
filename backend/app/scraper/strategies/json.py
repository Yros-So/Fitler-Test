import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.core.config import Settings
from app.scraper.http import HttpFetcher, normalize_shop_url
from app.scraper.parsing import parse_html
from app.scraper.types import ScrapedProduct, ScrapedVariant


class JSONStrategy:
    """Stratégie JSON embarqué : parse les données injectées dans le HTML.

    Certains thèmes (notamment headless/Next.js) ne fournissent pas
    /products.json : les données produits sont alors sérialisées dans les
    balises <script> de la page. On les récupère via ShopifyAnalytics
    (boutiques classiques) ou via le JSON __NEXT_DATA__/RSC (sites headless).
    """

    name = "json"

    def __init__(self, settings: Settings, fetcher: HttpFetcher | None = None) -> None:
        self.settings = settings
        self.fetcher = fetcher or HttpFetcher(settings)

    def scrape(self, base_url: str) -> list[ScrapedProduct]:
        base = normalize_shop_url(base_url)
        with self.fetcher.client() as client:
            response = self.fetcher.get(client, base)
        return self.parse_embedded_products(response.text, base)

    def parse_embedded_products(self, html: str, base_url: str) -> list[ScrapedProduct]:
        soup = parse_html(html)
        products: list[ScrapedProduct] = []

        # Chaque balise <script> peut contenir des données produits
        # sous différents formats : on les essaie tous.
        for script in soup.find_all("script"):
            text = script.string or script.get_text() or ""
            products.extend(self._parse_shopify_analytics(text, base_url))
            products.extend(self._parse_next_data(text, base_url))

        # Un même produit peut apparaître dans les deux formats : dédup.
        deduped: dict[str, ScrapedProduct] = {}
        for product in products:
            deduped.setdefault(product.handle, product)
        return list(deduped.values())

    def _parse_shopify_analytics(self, text: str, base_url: str) -> list[ScrapedProduct]:
        # ShopifyAnalytics.meta.product = {...} : objet JS assigné en clair.
        match = re.search(r"ShopifyAnalytics\.meta\.product\s*=\s*(\{.*?\});", text, re.S)
        if not match:
            return []
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return []

        handle = str(payload.get("handle") or payload.get("id") or "product")
        variants = [
            ScrapedVariant(
                external_id=str(variant.get("id")) if variant.get("id") is not None else None,
                title=str(variant.get("name") or variant.get("public_title") or "Default"),
                sku=variant.get("sku") or None,
                price=variant.get("price"),
                available=bool(variant.get("available", False)),
                options={},
            )
            for variant in payload.get("variants", [])
            if isinstance(variant, dict)
        ]
        return [
            ScrapedProduct(
                external_id=str(payload.get("id")) if payload.get("id") is not None else None,
                name=str(payload.get("title") or handle),
                price=variants[0].price if variants else payload.get("price"),
                description=None,
                image_urls=[],
                vendor=payload.get("vendor"),
                tags=[],
                handle=handle,
                url=urljoin(base_url, f"/products/{handle}"),
                options={},
                variants=variants,
            )
        ]

    def _parse_next_data(self, text: str, base_url: str) -> list[ScrapedProduct]:
        # Bloc JSON (Next.js data) complet : on vérifie la présence de
        # "props"/"product" avant d'essayer de le décoder.
        if '"props"' not in text or '"product"' not in text:
            return []
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return []
        # Parcours récursif du JSON : on récolte tout dictionnaire qui
        # ressemble à un produit (title+handle ou name+price).
        matches: list[dict] = []
        self._collect_product_like_dicts(payload, matches)
        products: list[ScrapedProduct] = []
        for item in matches:
            handle = str(item.get("handle") or item.get("slug") or item.get("id") or "product")
            products.append(
                ScrapedProduct(
                    external_id=str(item.get("id")) if item.get("id") is not None else None,
                    name=str(item.get("title") or item.get("name") or handle),
                    price=item.get("price") or item.get("min_price"),
                    description=item.get("description"),
                    image_urls=self._extract_images(item),
                    vendor=item.get("vendor") or item.get("brand"),
                    tags=item.get("tags") if isinstance(item.get("tags"), list) else [],
                    handle=handle,
                    url=urljoin(base_url, f"/products/{handle}"),
                    options=item.get("options") if isinstance(item.get("options"), dict) else {},
                    variants=[],
                )
            )
        return products

    def _collect_product_like_dicts(self, value: object, matches: list[dict]) -> None:
        # Parcours en profondeur : dès qu'un nœud ressemble à un produit,
        # on le capture et on ne descend plus dans ses enfants.
        if isinstance(value, dict):
            keys = set(value)
            if {"title", "handle"} <= keys or {"name", "price"} <= keys:
                matches.append(value)
                return
            for child in value.values():
                self._collect_product_like_dicts(child, matches)
        elif isinstance(value, list):
            for child in value:
                self._collect_product_like_dicts(child, matches)

    @staticmethod
    def _extract_images(item: dict) -> list[str]:
        # Les images peuvent être une liste de chaînes ou d'objets {src/url}.
        images = item.get("images") or item.get("media") or []
        if not isinstance(images, list):
            return []
        urls: list[str] = []
        for image in images:
            if isinstance(image, str):
                urls.append(image)
            elif isinstance(image, dict):
                url = image.get("src") or image.get("url")
                if url:
                    urls.append(str(url))
        return urls
