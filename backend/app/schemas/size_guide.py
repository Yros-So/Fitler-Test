from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SizeGuideRead(BaseModel):
    id: str
    website_id: str
    product_id: str | None
    title: str
    source_url: str
    content: dict
    raw_text: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SizeGuideListResponse(BaseModel):
    items: list[SizeGuideRead]
    total: int
    page: int
    page_size: int
