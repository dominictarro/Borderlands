"""Enumerations that need to be shared between modules.
"""

import enum


class EvidenceSource(enum.Enum):
    """The site the Oryx loss references as evidence of the status."""

    POST_IMG = "postimg"
    TWITTER = "twitter"
    OTHER = "other"


class MediaType(enum.Enum):
    """The type of media."""

    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    UNKNOWN = "unknown"


class LossDateInferenceMethod(enum.StrEnum):
    """The method used to infer the date of the equipment loss."""
