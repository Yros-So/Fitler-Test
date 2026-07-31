from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Shopify Product & Size Guide Scraper"
    api_prefix: str = ""
    database_url: str = "sqlite:///./dev.db"
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    auto_create_tables: bool = True
    request_timeout_seconds: float = 20.0
    request_retries: int = 3
    max_shopify_pages: int = 10
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    public_base_url: AnyHttpUrl | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SCRAPER_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
