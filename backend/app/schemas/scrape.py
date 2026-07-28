from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict

ScrapeStatus = Literal["pending", "running", "completed", "failed"]


class ScrapeRequest(BaseModel):
    url: AnyHttpUrl


class ScrapeJobQueued(BaseModel):
    job_id: str


class ScrapeJobRead(BaseModel):
    id: str
    website_id: str
    status: ScrapeStatus
    error: str | None
    started_at: datetime | None
    finished_at: datetime | None
    stats: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
