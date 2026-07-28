import json
from decimal import Decimal

from app.models.product import Product


def _default(value: object) -> str:
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def products_to_json(products: list[Product]) -> bytes:
    payload = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "vendor": product.vendor,
            "handle": product.handle,
            "url": product.url,
            "images": product.image_urls,
            "tags": product.tags,
            "variants": [
                {
                    "id": variant.id,
                    "title": variant.title,
                    "sku": variant.sku,
                    "price": variant.price,
                    "available": variant.available,
                    "options": variant.options,
                }
                for variant in product.variants
            ],
        }
        for product in products
    ]
    return json.dumps(payload, default=_default, ensure_ascii=False, indent=2).encode("utf-8")
