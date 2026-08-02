import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.core.config import Settings
from app.scraper.http import HttpFetcher, normalize_shop_url
from app.scraper.parsing import parse_html
from app.scraper.types import ScrapedSizeGuide

# Mots-clés (FR/EN) indiquant une page ou un bloc de guide des tailles.
SIZE_PATTERN = re.compile(
    r"(size|sizing|guide|chart|fit|measurement|taille|pointure|mesure)",
    re.I,
)


class SizeGuideHTMLStrategy:
    """Détection et extraction des guides de taille.

    Démarche : on part de la page d'accueil, on repère les liens dont le
    libellé évoque un guide des tailles, puis on visite ces pages (plus des
    chemins courants) pour extraire les tableaux de mesures normalisés.
    """

    name = "size_guide"

    def __init__(self, settings: Settings, fetcher: HttpFetcher | None = None) -> None:
        self.settings = settings
        self.fetcher = fetcher or HttpFetcher(settings)

    def scrape(self, base_url: str) -> list[ScrapedSizeGuide]:
        base = normalize_shop_url(base_url)
        with self.fetcher.client() as client:
            try:
                home = self.fetcher.get(client, base)
            except Exception:
                # Page d'accueil inaccessible (429/erreur réseau) : on ne
                # peut rien détecter, on abandonne sans faire échouer le job.
                return []
            soup = parse_html(home.text)
            # Liens candidats détectés + chemins standard si absents.
            candidate_urls = self._candidate_urls(soup, base)

            guides: list[ScrapedSizeGuide] = []
            for url in candidate_urls[:12]:
                try:
                    response = self.fetcher.get(client, url)
                except Exception:
                    # Page introuvable/indisponible : on passe au lien suivant.
                    continue
                page = parse_html(response.text)
                guide = self.parse_page(page, url)
                if guide:
                    guides.append(guide)

        # Un même guide peut être atteint via plusieurs URLs : dédup.
        deduped: dict[tuple[str, str], ScrapedSizeGuide] = {}
        for guide in guides:
            deduped.setdefault((guide.title.lower(), guide.source_url), guide)
        return list(deduped.values())

    def parse_page(self, soup: BeautifulSoup, source_url: str) -> ScrapedSizeGuide | None:
        # Un guide "valide" contient soit des tableaux de mesures, soit un
        # bloc de texte porteur de mots-clés taille/mesure.
        tables = self.extract_tables(soup)
        text_blocks = self._size_related_blocks(soup)
        if not tables and not text_blocks:
            return None

        title = self._title(soup)
        text = "\n\n".join(text_blocks)[:6000] if text_blocks else None
        return ScrapedSizeGuide(
            title=title,
            source_url=source_url,
            text=text,
            tables=tables,
            source_type="html",
            metadata={
                "signals": self._signals(soup),
                "table_count": len(tables),
            },
        )

    def extract_tables(self, soup: BeautifulSoup) -> list[list[list[str]]]:
        # Extrait les tableaux HTML et ne garde que ceux qui ressemblent à
        # une grille de tailles (mots-clés ou unités de mesure).
        tables: list[list[list[str]]] = []
        for table in soup.find_all("table"):
            rows: list[list[str]] = []
            for row in table.find_all("tr"):
                cells = [
                    cell.get_text(" ", strip=True)
                    for cell in row.find_all(["th", "td"])
                    if cell.get_text(" ", strip=True)
                ]
                if cells:
                    rows.append(cells)
            if rows and self._looks_like_size_table(rows):
                tables.append(rows)
        return tables

    def _candidate_urls(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        urls: list[str] = [base_url]
        # 1) Liens dont le libellé (texte + href + aria-label) évoque la taille.
        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            label = " ".join(
                [anchor.get_text(" ", strip=True), href or "", anchor.get("aria-label") or ""]
            )
            if href and SIZE_PATTERN.search(label):
                url = urljoin(base_url, href.split("#")[0]).rstrip("/")
                if url not in urls:
                    urls.append(url)
        # 2) Chemins canoniques Shopify souvent utilisés pour ces pages.
        common_paths = [
            "/pages/size-guide",
            "/pages/sizing-guide",
            "/pages/guide-des-tailles",
            "/pages/size-chart",
        ]
        for path in common_paths:
            url = urljoin(base_url, path).rstrip("/")
            if url not in urls:
                urls.append(url)
        return urls

    def _size_related_blocks(self, soup: BeautifulSoup) -> list[str]:
        # Blocs de texte (section, div, accordéon, popup) porteurs de
        # mots-clés taille, bornés en longueur pour éviter le bruit.
        blocks: list[str] = []
        for node in soup.find_all(["section", "div", "article", "details", "dialog"]):
            if not isinstance(node, Tag):
                continue
            text = node.get_text(" ", strip=True)
            if 30 <= len(text) <= 3000 and SIZE_PATTERN.search(text):
                blocks.append(text)
        return blocks[:10]

    @staticmethod
    def _looks_like_size_table(rows: list[list[str]]) -> bool:
        # Heuristique : présence d'un mot-clé taille OU d'une unité de
        # mesure (XS/S/M/L, cm, inch) dans la table.
        flattened = " ".join(cell for row in rows for cell in row)
        has_size_word = bool(SIZE_PATTERN.search(flattened))
        has_measurement = bool(re.search(r"\b(xs|s|m|l|xl|xxl|\d{2,3}\s?cm|\d{1,2}\s?in)\b", flattened, re.I))
        return has_size_word or has_measurement

    @staticmethod
    def _title(soup: BeautifulSoup) -> str:
        # Titre du guide : heading principal, sinon balise <title>.
        heading = soup.find(["h1", "h2"])
        if heading and heading.get_text(strip=True):
            return heading.get_text(" ", strip=True)[:512]
        if soup.title and soup.title.string:
            return soup.title.string.strip()[:512]
        return "Size guide"

    @staticmethod
    def _signals(soup: BeautifulSoup) -> list[str]:
        # Signaux de mise en page détectés (tableau, popup, accordéon,
        # hook JS) : utiles pour qualifier le guide extrait.
        signals: list[str] = []
        for selector, label in [
            ("table", "html_table"),
            ("dialog", "popup"),
            ("details", "accordion"),
            ('[data-size-guide], [data-size-chart]', "javascript_hook"),
        ]:
            if soup.select(selector):
                signals.append(label)
        return signals
