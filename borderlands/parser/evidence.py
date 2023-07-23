"""
Module for parsing equipment model HTML trees.
"""
from __future__ import annotations

import string
import traceback
from typing import Generator

from ..utilities.misc import parse_alphabet_items
from .base import ParserBase


class EvidenceParser(ParserBase):
    """
    Parses equipment losses with their evidence references.
    """

    @property
    def evidence_url(self) -> str | None:
        """Returns the 'href' of the <a> tag."""
        return self.tag.attrs.get("href")

    @property
    def text(self) -> str:
        """Description of the confirmation."""
        # :return: Text contents of the case entry
        # Entries have two components:
        #   1. the case id for the model
        #   2. the asset's status
        # Some have a third component
        #   3. the cause of status
        # Generally speaking, the entries are formatted like:
        #     - '{ids}, {statuses}'
        #     - '{ids}, with {causes}, {statuses}'
        #     - '{ids}, {statuses} by {causes}'
        return self.tag.text.strip("()")

    def parse(self) -> Generator[dict, None, None]:
        """Parses the <a> tag for the confirmed losses provided by the evidence0.

        :yield: A confirmation dictionary.
        """
        # Split instead of lex so the end of the IDs section can be detected
        text = self.text
        # NOTE need to remove duplicates here with set
        # For example: "26, with 23mm ZU-23, destroyed"
        #   will create [26, 23, 23]
        #   due to the 23mm
        numbers = parse_alphabet_items(text, alphabet=string.digits)
        for id_ in set(numbers):
            try:
                yield dict(
                    evidence_url=self.evidence_url, description=text, id_=int(id_)
                )
            except Exception:
                self.logger.error(traceback.format_exc())
