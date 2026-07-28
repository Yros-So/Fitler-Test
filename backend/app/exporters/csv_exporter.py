import csv
from io import StringIO

from app.models.product import Product


def products_to_csv(products: list[Product]) -> bytes:
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "product_id",
            "name",
            "price",
            "vendor",
            "handle",
            "url",
            "variant_id",
            "variant_title",
            "sku",
            "variant_price",
            "available",
        ],
    )
    writer.writeheader()
    for product in products:
        variants = product.variants or [None]
        for variant in variants:
            writer.writerow(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "vendor": product.vendor,
                    "handle": product.handle,
                    "url": product.url,
                    "variant_id": variant.id if variant else "",
                    "variant_title": variant.title if variant else "",
                    "sku": variant.sku if variant else "",
                    "variant_price": variant.price if variant else "",
                    "available": variant.available if variant else "",
                }
            )
    return buffer.getvalue().encode("utf-8-sig")
