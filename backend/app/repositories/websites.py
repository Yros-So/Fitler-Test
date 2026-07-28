from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.website import Website


def canonical_url(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return f"{scheme}://{netloc}{path}"


class WebsiteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create(self, url: str) -> Website:
        normalized = canonical_url(url)
        website = self.session.scalar(select(Website).where(Website.url == normalized))
        if website:
            return website

        parsed = urlparse(normalized)
        website = Website(url=normalized, domain=parsed.netloc)
        self.session.add(website)
        self.session.flush()
        return website
