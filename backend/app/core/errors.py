class ScraperError(Exception):
    """Base exception for scraper-specific failures."""


class FetchError(ScraperError):
    """Raised when a remote shop cannot be fetched."""


class ParseError(ScraperError):
    """Raised when a fetched shop response cannot be parsed."""
