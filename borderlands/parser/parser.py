"""
Generic parser for parsing the HTML of single and multi country Oryx loss pages.
"""
import logging
import re
from typing import Any, Generator

import bs4

from .article import ArticleParser
from .base import ParserBase


class OryxParser(ParserBase):
    """Parses Oryx equipment loss articles."""

    def __init__(
        self,
        soup: bs4.BeautifulSoup,
        multi: bool = False,
        logger: logging.Logger | None = None,
    ) -> None:
        self.soup: bs4.BeautifulSoup = soup
        # Find section starts
        super().__init__(self.body, logger)
        self._multi: bool = multi

    @property
    def body(self) -> bs4.Tag:
        """The body of the article.

        Returns
        -------
        bs4.Tag
            A `bs4.Tag` object containing the article's body
        """
        return self.soup.find(
            attrs={"class": "post-body entry-content", "itemprop": "articleBody"}
        )

    @staticmethod
    def _make_section_span(siblings: list[bs4.Tag]) -> bs4.Tag:
        """Makes a nested span of tags from a list of siblings."""
        level_1 = bs4.Tag(name="div")
        level_2 = bs4.Tag(name="div")
        level_1.append(level_2)
        for s in siblings:
            level_2.append(s)
        return level_1

    def _multi_parse(self) -> Generator[dict[str, Any], None, None]:
        """Parses the `tag`.

        Yields
        ------
        dict
            A standardized equipment loss case.
        """
        section_start_pattern = re.compile(
            r"^(Russia|Ukraine) \- \d+.+$", flags=re.DOTALL
        )

        # Identify the start of each country's section
        sections_starts: list[tuple[str, bs4.Tag]] = []
        for h3 in self.body.find_all("h3", recursive=True):
            h3: bs4.Tag
            m = section_start_pattern.match(h3.text)
            if m:
                sections_starts.append((m.group(1), h3))

        # Build the span of tags for each section
        # They have to be nested in two levels of divs to be compatible with ArticleParser
        sections: list[tuple[str, bs4.Tag]] = []
        for i, (country, start) in enumerate(sections_starts):
            start: bs4.Tag
            section = []
            for sibling in start.next_siblings:
                if sibling in [ss[1] for ss in sections_starts]:
                    sections.append((country, self._make_section_span(section)))
                    break
                else:
                    section.append(sibling)
            else:
                sections.append((country, self._make_section_span(section)))

        # Parse each section and add the country
        for country, section in sections:
            for case in ArticleParser(section, 0).parse():
                case["country"] = country
                yield case

    def _single_parse(
        self, data_section_index: int
    ) -> Generator[dict[str, Any], None, None]:
        """Parses the `tag`.

        Yields
        ------
        dict
            A standardized equipment loss case.
        """
        yield from ArticleParser(self.body, data_section_index).parse()

    def parse(
        self, data_section_index: int | None = None
    ) -> Generator[dict[str, Any], None, None]:
        if self._multi:
            yield from self._multi_parse()
        else:
            if data_section_index is None:
                raise ValueError(
                    "data_section_index must be specified when not parsing a multi-country article"
                )
            yield from self._single_parse(data_section_index)
