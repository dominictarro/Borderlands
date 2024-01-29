"""
Module for parsing equipment model HTML trees.
"""

from __future__ import annotations

import re
import traceback
from typing import Generator

from .base import ParserBase
from .evidence import EvidenceParser


class EquipmentModelParser(ParserBase):
    """
    Parses equipment model HTML trees for visually-confirmed equipment losses.
    """

    @property
    def country_of_production_flag_url(self) -> str | None:
        img = img = self.tag.find("img", recursive=True)
        return img.attrs.get("src", None)

    # Models are embedded in text like: "12 BRM-1K reconnaissance vehicle"
    # where that initial number denotes the total number of entries for the
    # model
    #
    # Irregular Example
    #   "  BTR-70"
    model_pattern = re.compile(
        r"^\s*(?P<entries>\d*)\s+(?P<model>.+)$", flags=re.DOTALL
    )

    @property
    def model(self) -> str:
        substring = self.tag.text.split(":", 1)[0]
        return self.model_pattern.match(substring).group("model")

    def parse(self) -> Generator[dict, None, None]:
        model = self.model
        country_of_production_flag_url = self.country_of_production_flag_url

        for tag in self.tag.find_all("a", recursive=True):
            try:
                for case in EvidenceParser(tag, logger=self.logger).parse():
                    # Set equipment model attributes
                    case["model"] = model
                    case["country_of_production_flag_url"] = (
                        country_of_production_flag_url
                    )
                    yield case
            except Exception:
                self.logger.error(traceback.format_exc())
