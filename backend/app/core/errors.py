class ScraperError(Exception):
    """Base exception for scraper-specific failures."""


class FetchError(ScraperError):
    """Raised when a remote shop cannot be fetched."""


class RateLimitedError(FetchError):
    """Raised when the remote shop rate-limits the request (HTTP 429).

    Porte l'éventuel délai suggéré par le serveur (en-tête ``Retry-After``)
    pour adapter le backoff lors des nouvelles tentatives.
    """

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ParseError(ScraperError):
    """Raised when a fetched shop response cannot be parsed."""
