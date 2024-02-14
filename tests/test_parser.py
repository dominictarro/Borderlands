"""
Tests for the article parser.
"""

import gzip
from pathlib import Path
from typing import TYPE_CHECKING

import bs4
import pytest

if TYPE_CHECKING:
    from borderlands.parser.article import ArticleParser


@pytest.fixture
def oryx_ukraine_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with gzip.open(test_data_path / "pages" / "ukraine.html.gz", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def oryx_russia_webpage(test_data_path: Path) -> bs4.Tag:
    """Path to the Oryx Ukraine webpage."""
    with gzip.open(test_data_path / "pages" / "russia.html.gz", "r") as fo:
        return bs4.BeautifulSoup(fo.read(), features="html.parser")


@pytest.fixture
def ukraine_article_parser(oryx_ukraine_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    from borderlands.parser.article import ArticleParser

    body = oryx_ukraine_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.parser.article import UKRAINE_DATA_SECTION_INDEX

    yield ArticleParser(body, UKRAINE_DATA_SECTION_INDEX)


@pytest.fixture
def russia_article_parser(oryx_russia_webpage: bs4.Tag) -> "ArticleParser":
    """An `ArticleParser` object."""
    from borderlands.parser.article import ArticleParser

    body = oryx_russia_webpage.find(
        attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
    )
    from borderlands.parser.article import RUSSIA_DATA_SECTION_INDEX

    yield ArticleParser(body, RUSSIA_DATA_SECTION_INDEX)


@pytest.fixture
def ukraine_page_parse_result(ukraine_article_parser: "ArticleParser") -> list:
    """The result of parsing the Ukraine page."""
    yield list(ukraine_article_parser.parse())


@pytest.fixture
def russia_page_parse_result(russia_article_parser: "ArticleParser") -> list:
    """The result of parsing the Russia page."""
    yield list(russia_article_parser.parse())


def test_ukraine_page_parse(ukraine_article_parser: "ArticleParser"):
    """Tests parsing the Ukraine page."""
    assert ukraine_article_parser
    result = list(ukraine_article_parser.parse())
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


def test_russia_page_parse(russia_article_parser: "ArticleParser"):
    """Tests parsing the Russia page."""
    assert russia_article_parser
    result = list(russia_article_parser.parse())
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


def test_ukraine_page_parse_result(ukraine_page_parse_result: list):
    """Tests the result of parsing the Ukraine page."""
    assert isinstance(ukraine_page_parse_result, list)
    assert all(isinstance(item, dict) for item in ukraine_page_parse_result)

    EXPECTED_KEYS = {
        "evidence_url",
        "description",
        "id_",
        "model",
        "country_of_production_flag_url",
        "category",
    }
    assert all(
        EXPECTED_KEYS.issubset(item.keys()) for item in ukraine_page_parse_result
    )

    # Test types
    assert all(
        isinstance(item["evidence_url"], str) for item in ukraine_page_parse_result
    )
    assert all(
        isinstance(item["description"], str) for item in ukraine_page_parse_result
    )
    assert all(isinstance(item["id_"], int) for item in ukraine_page_parse_result)
    assert all(isinstance(item["model"], str) for item in ukraine_page_parse_result)
    assert all(
        isinstance(item["country_of_production_flag_url"], str)
        for item in ukraine_page_parse_result
    )
    assert all(isinstance(item["category"], str) for item in ukraine_page_parse_result)


def test_russia_page_parse_result(russia_page_parse_result: list):
    """Tests the result of parsing the Russia page."""
    assert isinstance(russia_page_parse_result, list)
    assert all(isinstance(item, dict) for item in russia_page_parse_result)

    EXPECTED_KEYS = {
        "evidence_url",
        "description",
        "id_",
        "model",
        "country_of_production_flag_url",
        "category",
    }
    assert all(EXPECTED_KEYS.issubset(item.keys()) for item in russia_page_parse_result)

    # Test types
    assert all(
        isinstance(item["evidence_url"], str) for item in russia_page_parse_result
    )
    assert all(
        isinstance(item["description"], str) for item in russia_page_parse_result
    )
    assert all(isinstance(item["id_"], int) for item in russia_page_parse_result)
    assert all(isinstance(item["model"], str) for item in russia_page_parse_result)
    assert all(
        isinstance(item["country_of_production_flag_url"], str)
        for item in russia_page_parse_result
    )
    assert all(isinstance(item["category"], str) for item in russia_page_parse_result)
