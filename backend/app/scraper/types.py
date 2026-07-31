from dataclasses import dataclass, field
from typing import Protocol


# Structures de données "brutes" produites par le scraper, indépendantes de
# la base de données. Elles servent d'interface entre les stratégies
# d'extraction et la couche de persistance (CatalogRepository).
@dataclass(slots=True)
class ScrapedVariant:
    external_id: str | None
    title: str
    sku: str | None
    price: str | float | int | None
    available: bool
    options: dict = field(default_factory=dict)


@dataclass(slots=True)
class ScrapedProduct:
    external_id: str | None
    name: str
    price: str | float | int | None
    description: str | None
    image_urls: list[str]
    vendor: str | None
    tags: list[str]
    handle: str
    url: str
    options: dict = field(default_factory=dict)
    variants: list[ScrapedVariant] = field(default_factory=list)


@dataclass(slots=True)
class ScrapedSizeGuide:
    title: str
    source_url: str
    text: str | None
    tables: list[list[list[str]]] = field(default_factory=list)
    source_type: str = "html"
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class ScrapeResult:
    products: list[ScrapedProduct] = field(default_factory=list)
    size_guides: list[ScrapedSizeGuide] = field(default_factory=list)


# Protocoles : contrat qu'une stratégie d'extraction doit respecter pour
# pouvoir être branchée sur le moteur (extensible à d'autres CMS).
class ProductStrategy(Protocol):
    name: str

    def scrape(self, base_url: str) -> list[ScrapedProduct]:
        ...


class SizeGuideStrategy(Protocol):
    name: str

    def scrape(self, base_url: str) -> list[ScrapedSizeGuide]:
        ...
