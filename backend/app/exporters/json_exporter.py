import json
from decimal import Decimal

from app.models.product import Product


def _default(value: object) -> str:
    # Sérialise les types non-JSON (ex. Decimal) en chaîne.
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def products_to_json(products: list[Product]) -> bytes:
    """Export complet (produits + variantes + images) au format JSON."""
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
    # ensure_ascii=False : conserve les accents ; indent=2 : lisible.
    return json.dumps(payload, default=_default, ensure_ascii=False, indent=2).encode("utf-8")
