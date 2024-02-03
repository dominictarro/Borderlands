import pytest

from borderlands.utilities.misc import (
    parse_alphabet_items,
    series_splitter,
)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("a, b, c, and d", ["a", "b", "c", "and", "d"]),
        ("a, b, c or d", ["a", "b", "c", "or", "d"]),
        ("xyz", ["xyz"]),
    ],
)
def test_parse_alphabet_items(text: str, expected: list[str]):
    assert parse_alphabet_items(text) == expected


def test_parse_alphabet_items_exclude():
    assert parse_alphabet_items("a, b, c, and d", exclude=True) == [
        ", ",
        ", ",
        ", ",
        " ",
    ]


def test_parse_alphabet_items_custom_alphabet():
    assert parse_alphabet_items("a, b, c, and d", alphabet="abc") == [
        "a",
        "b",
        "c",
        "a",
    ]


def test_series_splitter():
    assert series_splitter("a, b, c, and d") == ["a", "b", "c", "d"]
    assert series_splitter("a, b, c or d") == ["a", "b", "c", "d"]


def test_series_splitter_delimiter():
    assert series_splitter("a\t b\t c\t or d", delimiter="\t") == ["a", "b", "c", "d"]
