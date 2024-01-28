"""
Tags for the fields in the schema.
"""

import enum


class Tag(enum.Enum):
    """A class to hold all tags for the fields."""

    attribute = "attribute"
    context = "context"
    debug = "debug"
    dimension = "dimension"
    equipment = "equipment"
    inherited = "inherited"
    media = "media"
    metadata = "metadata"

    def __eq__(self, __value: object) -> bool:
        """Overrides the equality operator to allow for string comparison."""
        if isinstance(__value, str):
            return self.value == __value
        elif isinstance(__value, Tag):
            return self.value == __value.value
        return super().__eq__(__value)


TagSet = list[Tag | str]
