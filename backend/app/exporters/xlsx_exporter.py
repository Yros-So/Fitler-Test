from io import BytesIO

from openpyxl import Workbook

from app.models.product import Product


def products_to_xlsx(products: list[Product]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Products"
    sheet.append(
        [
            "Product ID",
            "Name",
            "Price",
            "Vendor",
            "Handle",
            "URL",
            "Variant ID",
            "Variant",
            "SKU",
            "Variant Price",
            "Available",
        ]
    )

    for product in products:
        variants = product.variants or [None]
        for variant in variants:
            sheet.append(
                [
                    product.id,
                    product.name,
                    float(product.price) if product.price is not None else None,
                    product.vendor,
                    product.handle,
                    product.url,
                    variant.id if variant else None,
                    variant.title if variant else None,
                    variant.sku if variant else None,
                    float(variant.price) if variant and variant.price is not None else None,
                    variant.available if variant else None,
                ]
            )

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()
