from urllib.parse import urlparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.errors import FetchError


def normalize_shop_url(url: str) -> str:
    # Normalise l'URL saisie (ajout de https:// si absent, suppression du
    # slash final) pour servir de clé stable en base et d'URL de requête.
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if not parsed.netloc:
        raise FetchError(f"Invalid URL: {url}")
    return f"{parsed.scheme or 'https'}://{parsed.netloc}{parsed.path.rstrip('/')}"


class HttpFetcher:
    """Client HTTP partagé par toutes les stratégies de scraping."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def client(self) -> httpx.Client:
        return httpx.Client(
            follow_redirects=True,
            timeout=self.settings.request_timeout_seconds,
            # User-Agent réaliste : évite d'être bloqué en tant que bot.
            headers={"User-Agent": self.settings.user_agent},
        )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.4, min=0.4, max=4),
        reraise=True,
    )
    def get(self, client: httpx.Client, url: str) -> httpx.Response:
        # Récupère une page avec retry exponentiel en cas de timeout/réseau,
        # ce qui rend le scraper robuste aux baisses de connectivité.
        try:
            response = client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            # 4xx/5xx : levée dédiée, rattrapée par la stratégie appelante.
            raise FetchError(f"HTTP {exc.response.status_code} for {url}") from exc
        except httpx.HTTPError as exc:
            raise FetchError(f"Failed to fetch {url}: {exc}") from exc
