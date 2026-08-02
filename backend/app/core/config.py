from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application, surchargeable par variables
    d'environnement préfixées SCRAPER_ (ex. SCRAPER_DATABASE_URL)."""

    app_name: str = "Shopify Product & Size Guide Scraper"
    api_prefix: str = ""
    database_url: str = "sqlite:///./dev.db"  # SQLite en local, PG en prod
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    auto_create_tables: bool = True
    request_timeout_seconds: float = 20.0
    request_retries: int = 3
    max_shopify_pages: int = 10
    # Proxy HTTP(S) optionnel (SCRAPER_PROXY_URL). Utile depuis une IP de
    # datacenter (Render) bloquée par certaines boutiques : permet de passer
    # par une IP de contournement.
    proxy_url: str | None = None
    # User-Agent réaliste de navigateur : évite que les boutiques
    # bloquent le scraping (une UA de bot déclenche des réponses 403/429).
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
    # Instanciée une seule fois (cache) : lecture unique du .env et
    # des variables d'environnement au démarrage.
    return Settings()
