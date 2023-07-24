"""
Parses Oryx Articles.

"""
from __future__ import annotations

import logging
import re
import traceback
from typing import TYPE_CHECKING, Any, Generator

from .base import ParserBase
from .equipment_category import EquipmentCategoryParser

if TYPE_CHECKING:
    import bs4


RUSSIA_DATA_SECTION_INDEX = 7
UKRAINE_DATA_SECTION_INDEX = 1


class ArticleParser(ParserBase):
    """Parses Oryx equipment loss articles."""

    # Initialize
    _data_section_index: int

    def __init__(
        self,
        tag: bs4.Tag,
        _data_section_index: int,
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(tag, logger)
        self._data_section_index: int = _data_section_index

    @property
    def article_sections(self) -> bs4.ResultSet:
        """Sections of the article.

        Returns
        -------
        bs4.ResultSet
            A `bs4.ResultSet` object containing the article's sections
        """
        return self.tag.find_all("div", recursive=False)

    @property
    def data_section(self) -> bs4.Tag:
        """Section of the article containing core data.

        Returns
        -------
        bs4.Tag
            A `bs4.Tag` object containing core data
        """
        return self.article_sections[self._data_section_index]

    @property
    def equipment_category_sections(self) -> list[bs4.Tag]:
        """Sections of the article containing equipment categories.

        Returns
        -------
        list[bs4.Tag]
            A list of `bs4.Tag` objects containing equipment categories
        """
        categories: list[bs4.Tag] = []
        category_header_regex: re.Pattern = re.compile(
            r"^.+\(\d+, .+\)\s*$", flags=re.DOTALL
        )
        for tag in self.data_section.find_all("h3"):
            if category_header_regex.match(tag.text) is not None:
                categories.append(tag)
        return categories

    def parse(self) -> Generator[dict[str, Any], None, None]:
        """Yields cases found in the `tag`.

        Yields
        ------
        dict[str, Any]
            A dictionary of case data
        """
        for tag in self.equipment_category_sections:
            try:
                for result in EquipmentCategoryParser(tag, logger=self.logger).parse():
                    yield result
            except Exception:
                self.logger.error(traceback.format_exc())
