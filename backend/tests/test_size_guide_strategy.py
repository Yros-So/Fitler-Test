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
