from bs4 import BeautifulSoup

from app.core.config import Settings
from app.scraper.strategies.size_guide import SizeGuideHTMLStrategy, is_guide_page


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


def test_rejects_product_page_without_table() -> None:
    # Page produit mentionnant la taille mais sans tableau : faux positif,
    # ne doit plus être enregistrée comme guide.
    html = """
    <html>
      <body>
        <h1>Derbies cuir noir</h1>
        <div>Disponible également du 35 au 46.</div>
        <div>Composition et fabrication</div>
      </body>
    </html>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    guide = strategy.parse_page(BeautifulSoup(html, "html.parser"), "https://shop.example.com/products/pastani-noir")
    assert guide is None


def test_keeps_text_only_guide_page() -> None:
    # Page explicitement dédiée aux tailles sans tableau exploitable
    # (mesures en images/blocs) : conservée avec son texte.
    html = """
    <html>
      <body>
        <h1>Guide des tailles</h1>
        <div>Mesurez votre pied : posez-le sur une feuille et tracez son contour.</div>
      </body>
    </html>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    guide = strategy.parse_page(BeautifulSoup(html, "html.parser"), "https://shop.example.com/pages/guide-des-tailles")
    assert guide is not None
    assert guide.tables == []
    assert guide.text and "Mesurez" in guide.text


def test_keeps_table_anywhere_on_page() -> None:
    # Un tableau de mesures sur une page produit (ex. guide par produit)
    # reste toujours conservé.
    html = """
    <html>
      <body>
        <h1>Derbies cuir noir</h1>
        <table>
          <tr><th>EU</th><th>UK</th></tr>
          <tr><td>39</td><td>6</td></tr>
        </table>
      </body>
    </html>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    guide = strategy.parse_page(BeautifulSoup(html, "html.parser"), "https://shop.example.com/products/pastani-noir")
    assert guide is not None
    assert len(guide.tables) == 1


def test_is_guide_page() -> None:
    assert is_guide_page("Guide des tailles", "https://shop.example.com/pages/x")
    assert is_guide_page("Size guide", "https://shop.example.com/pages/x")
    assert is_guide_page("N/A", "https://shop.example.com/pages/guide-des-pointures")
    assert not is_guide_page("GUIDE D'ENTRETIEN", "https://shop.example.com/pages/guide-dentretien")
    assert not is_guide_page("Derbies cuir noir", "https://shop.example.com/products/pastani-noir")


def test_candidate_urls_include_french_pointures() -> None:
    # Le chemin canonique /pages/guide-des-pointures (utilisé par andre.fr)
    # doit être proposé même sans lien détecté sur la page d'accueil.
    strategy = SizeGuideHTMLStrategy(Settings())
    urls = strategy._candidate_urls(BeautifulSoup("<html><body></body></html>", "html.parser"), "https://www.andre.fr")
    assert "https://www.andre.fr/pages/guide-des-pointures" in urls
    assert "https://www.andre.fr/pages/guide-des-tailles" in urls


def test_candidate_urls_ignore_pdf_links() -> None:
    # Un lien "Guide des tailles" pointant vers un PDF ne doit pas être
    # suivi : pas de tableau HTML exploitable dans un fichier.
    html = """
    <html><body>
      <a href="https://cdn.shopify.com/s/files/GuideDesTailles.pdf?v=1645810092">Guide des tailles</a>
      <a href="/pages/size-guide">Size guide</a>
    </body></html>
    """
    strategy = SizeGuideHTMLStrategy(Settings())
    urls = strategy._candidate_urls(BeautifulSoup(html, "html.parser"), "https://www.andre.fr")
    assert not any(u.endswith(".pdf") for u in urls)
    assert "https://www.andre.fr/pages/size-guide" in urls
