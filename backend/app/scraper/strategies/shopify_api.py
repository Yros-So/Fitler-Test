from app.core.config import Settings
from app.scraper.http import HttpFetcher, normalize_shop_url
from app.scraper.parsing import parse_html
from app.scraper.types import ScrapedProduct, ScrapedVariant


class ShopifyAPIStrategy:
    name = "shopify_api"

    def __init__(self, settings: Settings, fetcher: HttpFetcher | None = None) -> None:
        self.settings = settings
        self.fetcher = fetcher or HttpFetcher(settings)

    def scrape(self, base_url: str) -> list[ScrapedProduct]:
        base = normalize_shop_url(base_url)
        products: list[ScrapedProduct] = []
        with self.fetcher.client() as client:
            for page in range(1, self.settings.max_shopify_pages + 1):
                endpoint = f"{base}/products.json?limit=250&page={page}"
                try:
                    response = self.fetcher.get(client, endpoint)
                except Exception:
                    if page == 1:
                        return []
                    break

                payload = response.json()
                page_products = payload.get("products", [])
                if not page_products:
                    break
                products.extend(self.parse_products(page_products, base))

        return products

    @staticmethod
    def parse_products(products_payload: list[dict], base_url: str) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        for item in products_payload:
            handle = str(item.get("handle") or item.get("id") or "product")
            variants = [
                ScrapedVariant(
                    external_id=str(variant.get("id")) if variant.get("id") is not None else None,
                    title=str(variant.get("title") or variant.get("name") or "Default"),
                    sku=variant.get("sku") or None,
                    price=variant.get("price"),
                    available=bool(variant.get("available", False)),
                    options={
                        key: variant.get(key)
                        for key in ("option1", "option2", "option3")
                        if variant.get(key) is not None
                    },
                )
                for variant in item.get("variants", [])
            ]
            first_price = variants[0].price if variants else item.get("price")
            images = [
                image.get("src")
                for image in item.get("images", [])
                if isinstance(image, dict) and image.get("src")
            ]
            body_html = item.get("body_html")
            description = (
                parse_html(body_html).get_text(" ", strip=True)
                if body_html
                else None
            )
            tags = item.get("tags") or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

            products.append(
                ScrapedProduct(
                    external_id=str(item.get("id")) if item.get("id") is not None else None,
                    name=str(item.get("title") or handle),
                    price=first_price,
                    description=description,
                    image_urls=images,
                    vendor=item.get("vendor") or None,
                    tags=tags,
                    handle=handle,
                    url=f"{base_url}/products/{handle}",
                    options={
                        option.get("name"): option.get("values", [])
                        for option in item.get("options", [])
                        if isinstance(option, dict) and option.get("name")
                    },
                    variants=variants,
                )
            )
        return products
