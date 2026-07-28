# from bs4 import BeautifulSoup
# from bs4.exceptions import FeatureNotFound


# def parse_html(markup: str) -> BeautifulSoup:
#     try:
#         return BeautifulSoup(markup, "lxml")
#     except FeatureNotFound:
#         return BeautifulSoup(markup, "html.parser")

from bs4 import BeautifulSoup


def parse_html(markup: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(markup, "lxml")
    except Exception:
        return BeautifulSoup(markup, "html.parser")

