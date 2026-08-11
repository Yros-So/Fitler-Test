from bs4 import BeautifulSoup

from app.core.config import Settings
from app.scraper.strategies.size_guide import SizeGuideHTMLStrategy


def test_extracts_size_guide_table() -> None:
    html = """
    <html>
      <body>
        <h1>Guide des tailles</h1>
        <table>
          <tr><th>Taille</th><th>Tour de poitrine</th></tr>
          <tr><td>S</td><td>86 cm</td></tr>
          <tr><td>M</td><td>92 cm</td></tr>
        </table>
      </body>
    </html>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    guide = strategy.parse_page(BeautifulSoup(html, "html.parser"), "https://shop.example.com/pages/guide")

    assert guide is not None
    assert guide.title == "Guide des tailles"
    assert guide.tables[0][0] == ["Taille", "Tour de poitrine"]


def test_extracts_size_system_headers_table() -> None:
    # Tables kleman : en-têtes CM/EU/UK/US sans mot-clé "taille" ni unité
    # de mesure en toutes lettres. Doit être reconnue comme une grille.
    html = """
    <table>
      <thead>
        <tr><th>CM</th><th>EU</th><th>UK</th><th>US</th></tr>
      </thead>
      <tbody>
        <tr><td>24.7</td><td>39</td><td>6</td><td>6.5</td></tr>
        <tr><td>30</td><td>47</td><td>13.5</td><td>12.5</td></tr>
      </tbody>
    </table>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    tables = strategy.extract_tables(BeautifulSoup(html, "html.parser"))
    assert len(tables) == 1
    assert tables[0][0] == ["CM", "EU", "UK", "US"]


def test_extracts_data_cm_inches_table() -> None:
    # Tables kleman complètes : cellules portant data-cm/data-inches.
    html = """
    <table>
      <tr><th>CM</th><th>EU</th></tr>
      <tr><td data-cm="24.7" data-inches="9.72">24.7</td><td>39</td></tr>
    </table>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    tables = strategy.extract_tables(BeautifulSoup(html, "html.parser"))
    assert len(tables) == 1
    assert tables[0][1] == ["24.7", "39"]
