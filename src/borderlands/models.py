"""
Database models for the datasets.
"""

import datetime

from sqlmodel import Field, SQLModel

from borderlands.enums import EvidenceSource, LossDateInferenceMethod


class EquipmentLoss(SQLModel, table=True):
    """Denormalized model for equipment losses."""

    # Dimensions
    country: str = Field(
        primary_key=True,
        title="Country",
        description="The common name of country that suffered the equipment loss.",
    )
    category: str = Field(
        primary_key=True,
        title="Category",
        description="The equipment category as defined by Oryx.",
    )
    model: str = Field(
        primary_key=True,
        title="Model",
        description="The equipment model as defined by Oryx.",
    )
    url_hash: str = Field(
        primary_key=True,
        title="URL Hash",
        description="A SHA-256 hash of the `evidence_url`.",
    )
    case_id: int = Field(
        primary_key=True,
        title="Case ID",
        description=(
            "A special ID for discriminating equipment losses when their `country`, `category`, `model`, and `url_hash` are the same."
            " Order is determined by appearance in the source page."
        ),
    )

    # Statuses
    is_abandoned: bool = Field(
        title="Abandoned",
        description="The loss is due to abandonment.",
    )
    is_captured: bool = Field(
        title="Captured",
        description="The loss is due to a belligerent capturing the equipment.",
    )
    is_damaged: bool = Field(
        title="Damaged",
        description="The loss is due to damage.",
    )
    is_destroyed: bool = Field(
        title="Destroyed",
        description="The loss is due to irrepairable destruction.",
    )
    is_scuttled: bool = Field(
        title="Scuttled",
        description="The loss is due to scuttling. Only applies to naval equipment.",
    )
    is_stripped: bool = Field(
        title="Stripped",
        description="The equipment was stripped of parts.",
    )
    is_sunk: bool = Field(
        title="Sunk",
        description="The loss is due to sinking. Only applies to naval equipment.",
    )
    is_raised: bool = Field(
        title="Raised",
        description="The equipment was raised from the sea floor.",
    )

    # Attributes
    evidence_url: str = Field(
        title="Evidence URL",
        description="The URL to the evidence of the equipment loss. Derived from `oryx_evidence_url`.",
        nullable=False,
    )
    country_of_production: str = Field(
        title="Country of Production",
        description="The ISO Alpha-3 code of the country that produces the equipment.",
    )
    evidence_source: EvidenceSource = Field(
        None,
        title="Evidence Source",
        description="The source the Oryx loss references as evidence of the status.",
    )
    date_of_loss: datetime.date | None = Field(
        None,
        title="Date of Loss",
        description=(
            "The inferred date of the equipment loss. See `date_loss_inference_method` for the "
            "method used to generate this value."
        ),
    )

    # Source context
    country_of_production_flag_url: str = Field(
        None,
        title="Country of Production Flag URL",
        description="The URL to the flag of the country that produces the `model`.",
    )
    oryx_description: str | None = Field(
        None,
        title="Oryx Description",
        description="The description of the equipment loss as provided by Oryx.",
    )
    oryx_id: int | None = Field(
        None,
        title="Oryx ID",
        description="The ID of the equipment loss as provided by Oryx. Unreliable due to duplicates.",
    )
    oryx_evidence_url: str = Field(
        title="Oryx Evidence URL",
        description="The URL to the Oryx cites for the equipment loss.",
    )
    date_loss_inference_method: LossDateInferenceMethod | None = Field(
        None,
        title="Date Loss Inference Method",
        description="The ID of the method used to infer the date of the equipment loss.",
    )
    created_on: datetime.datetime = Field(
        title="As of Date",
        description="The date the row was added to the dataset.",
        default_factory=datetime.datetime.now,
        nullable=False,
    )
