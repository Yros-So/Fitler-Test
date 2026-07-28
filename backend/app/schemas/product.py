from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductVariantRead(BaseModel):
    id: str
    external_id: str | None
    title: str
    sku: str | None
    price: Decimal | None
    available: bool
    options: dict

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: str
    website_id: str
    external_id: str | None
    name: str
    price: Decimal | None
    description: str | None
    image_urls: list[str]
    vendor: str | None
    tags: list[str]
    handle: str
    url: str
    options: dict
    variants: list[ProductVariantRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    total: int
    page: int
    page_size: int
