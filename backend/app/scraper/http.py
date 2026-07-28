from urllib.parse import urlparse

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.core.errors import FetchError


def normalize_shop_url(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if not parsed.netloc:
        raise FetchError(f"Invalid URL: {url}")
    return f"{parsed.scheme or 'https'}://{parsed.netloc}{parsed.path.rstrip('/')}"


class HttpFetcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def client(self) -> httpx.Client:
        return httpx.Client(
            follow_redirects=True,
            timeout=self.settings.request_timeout_seconds,
            headers={"User-Agent": self.settings.user_agent},
        )

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.4, min=0.4, max=4),
        reraise=True,
    )
    def get(self, client: httpx.Client, url: str) -> httpx.Response:
        try:
            response = client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as exc:
            raise FetchError(f"HTTP {exc.response.status_code} for {url}") from exc
        except httpx.HTTPError as exc:
            raise FetchError(f"Failed to fetch {url}: {exc}") from exc
