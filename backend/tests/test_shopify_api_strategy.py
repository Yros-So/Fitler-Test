from app.scraper.strategies.shopify_api import ShopifyAPIStrategy


def test_parse_shopify_products_payload() -> None:
    products = ShopifyAPIStrategy.parse_products(
        [
            {
                "id": 101,
                "title": "Leather Boot",
                "handle": "leather-boot",
                "body_html": "<p>Durable boot</p>",
                "vendor": "Acme",
                "tags": "shoes, winter",
                "images": [{"src": "https://cdn.example.com/boot.jpg"}],
                "options": [{"name": "Size", "values": ["40", "41"]}],
                "variants": [
                    {
                        "id": 201,
                        "title": "40",
                        "sku": "BOOT-40",
                        "price": "129.90",
                        "available": True,
                        "option1": "40",
                    }
                ],
            }
        ],
        "https://shop.example.com",
    )

    assert len(products) == 1
    product = products[0]
    assert product.handle == "leather-boot"
    assert product.price == "129.90"
    assert product.tags == ["shoes", "winter"]
    assert product.variants[0].available is True
    assert product.variants[0].options == {"option1": "40"}
