from bs4 import BeautifulSoup


def parse_html(markup: str) -> BeautifulSoup:
    # Analyse HTML/XML : lxml en priorité (rapide), sinon fallback sur
    # le parseur natif "html.parser" si lxml n'est pas disponible.
    try:
        return BeautifulSoup(markup, "lxml")
    except Exception:
        return BeautifulSoup(markup, "html.parser")

