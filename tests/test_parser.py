"""
Tests for the article parser.
"""
from borderlands.oryx_parser.article import ArticleParser


def test_ukraine_page_parse(ukraine_article_parser: ArticleParser):
    """Tests parsing the Ukraine page."""
    assert ukraine_article_parser
    result = list(ukraine_article_parser.parse())
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)


def test_russia_page_parse(russia_article_parser: ArticleParser):
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
    assert all(
        isinstance(item["id_"], str) and item["id_"].isnumeric()
        for item in ukraine_page_parse_result
    )
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
    assert all(
        isinstance(item["id_"], str) and item["id_"].isnumeric()
        for item in russia_page_parse_result
    )
    assert all(isinstance(item["model"], str) for item in russia_page_parse_result)
    assert all(
        isinstance(item["country_of_production_flag_url"], str)
        for item in russia_page_parse_result
    )
    assert all(isinstance(item["category"], str) for item in russia_page_parse_result)
