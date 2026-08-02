from urllib.parse import urlparse

from curl_cffi import requests as cffi_requests
from curl_cffi.requests.exceptions import RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from app.core.config import Settings
from app.core.errors import FetchError, RateLimitedError


def normalize_shop_url(url: str) -> str:
    # Normalise l'URL saisie (ajout de https:// si absent, suppression du
    # slash final) pour servir de clé stable en base et d'URL de requête.
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if not parsed.netloc:
        raise FetchError(f"Invalid URL: {url}")
    return f"{parsed.scheme or 'https'}://{parsed.netloc}{parsed.path.rstrip('/')}"


def _retry_wait(retry_state: object) -> float:
    # Délai avant nouvelle tentative : respecte l'en-tête Retry-After quand
    # le serveur l'indique (429, plafonné à 20 s), sinon backoff exponentiel.
    exc = retry_state.outcome.exception()
    if isinstance(exc, RateLimitedError) and exc.retry_after:
        return min(float(exc.retry_after), 20)
    return min(2 ** retry_state.attempt_number, 30)


class HttpFetcher:
    """Client HTTP partagé par toutes les stratégies de scraping.

    S'appuie sur ``curl_cffi`` en mode ``impersonate="chrome"`` : la plupart
    des boutiques Shopify sont protégées par Cloudflare, qui bloque les
    clients HTTP classiques (httpx/requests) sur leur empreinte TLS (JA3)
    avec une réponse 429. En imitant l'empreinte d'un vrai navigateur, on
    passe cette protection.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def client(self) -> cffi_requests.Session:
        # Session "impersonate chrome" : empreinte TLS + ordre des en-têtes
        # HTTP/2 identiques à Chrome.
        session = cffi_requests.Session(impersonate="chrome")
        session.headers.update(
            {
                # User-Agent réaliste et en-têtes d'un vrai navigateur.
                "User-Agent": self.settings.user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
        )
        if self.settings.proxy_url:
            # Proxy optionnel (SCRAPER_PROXY_URL) : contourner les blocages
            # par IP quand le réseau d'hébergement est réputé "datacenter".
            session.proxies.update(
                {
                    "http": self.settings.proxy_url,
                    "https": self.settings.proxy_url,
                }
            )
        return session

    @retry(
        retry=retry_if_exception_type(
            (RequestException, RateLimitedError)
        ),
        stop=stop_after_attempt(3),
        wait=_retry_wait,
        reraise=True,
    )
    def get(self, client: cffi_requests.Session, url: str) -> cffi_requests.Response:
        # Récupère une page avec retry (erreur réseau / 429) : rend le scraper
        # robuste aux baisses de connectivité et au rate limiting.
        response = client.get(url, timeout=self.settings.request_timeout_seconds)

        if response.status_code == 429:
            # Limite de débit atteinte : on tente à nouveau après un délai
            # (Retry-After si fourni, sinon backoff exponentiel).
            retry_after = response.headers.get("Retry-After")
            delay = None
            if retry_after and retry_after.isdigit():
                delay = float(retry_after)
            raise RateLimitedError(f"HTTP 429 for {url}", retry_after=delay)

        if response.status_code >= 400:
            # 4xx/5xx : levée dédiée, rattrapée par la stratégie appelante.
            raise FetchError(f"HTTP {response.status_code} for {url}")

        return response
