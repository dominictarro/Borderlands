"""
Module for parsing equipment category HTML trees.
"""

from __future__ import annotations

import re
import traceback
from typing import TYPE_CHECKING, Generator

from .base import ParserBase
from .equipment_model import EquipmentModelParser

if TYPE_CHECKING:
    import bs4


class EquipmentCategoryParser(ParserBase):
    """
    Parses equipment category HTML trees for visually-confirmed equipment
    losses.
    """

    label_pattern: re.Pattern = re.compile(r"^(?P<asset_category>.+?)\s\(\d+,.*")

    @property
    def label(self) -> str:
        """The label for the equipment category."""
        h3 = self.tag.text.strip()
        match = self.label_pattern.match(h3)
        return match.group("asset_category").strip()

    def parse(self) -> Generator[dict, None, None]:
        label = self.label
        ul_tag: bs4.Tag = self.tag.find_next("ul")
        for tag in ul_tag.find_all("li", recursive=False):
            try:
                for case in EquipmentModelParser(tag, logger=self.logger).parse():
                    # Set asset category attributes
                    case["category"] = label
                    yield case
            except Exception:
                self.logger.error(traceback.format_exc())
