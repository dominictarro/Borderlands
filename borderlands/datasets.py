"""
All datasets being released are defined in this file. This allows for a single
source of truth and easier referencing.
"""
import dataclasses as dc


@dc.dataclass
class Dataset:
    """Dataset class for storing dataset information.

    Attributes:
        label (str): The label for the dataset.
        host_bucket (str): The host bucket to fetch the dataset from.
        release_path (str): The path to release the dataset to.

    """

    label: str
    host_bucket: str
    release_path: str


oryx = Dataset(
    label="Oryx",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/oryx.parquet",
)

media_inventory = Dataset(
    label="Media Inventory",
    host_bucket="s3-bucket-borderlands-core",
    release_path="releases/media-inventory.parquet",
)
