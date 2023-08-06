"""
All datasets being released are defined in this file. This allows for a single
source of truth and easier referencing.
"""
import dataclasses as dc
import io

import polars as pl

from .. import blocks
from .formatter import Formatter
from .schema import FieldFilter, Schema


@dc.dataclass
class Dataset:
    """Dataset class for storing dataset information.

    Attributes:
        label (str): The label for the dataset.
        host_bucket (str): The host bucket to fetch the dataset from.
        release_path (str): The path to release the dataset to.
        schema (Schema): The schema for the dataset.

    """

    label: str
    host_bucket: str
    release_path: str
    schema: Schema
    description: str = dc.field(default_factory=str)

    def read(
        self, include: FieldFilter | None = None, exclude: FieldFilter | None = None
    ) -> pl.DataFrame:
        """Read the dataset's latest release.

        Args:
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            pl.DataFrame: The dataset's latest release.
        """
        with io.BytesIO() as f:
            blocks.core_bucket.download_object_to_file_object(self.release_path, f)
            f.seek(0)
            return pl.read_parquet(f).select(self.schema.columns(include, exclude))

    def to_markdown(
        self,
        level: int = 2,
        include: FieldFilter | None = None,
        exclude: FieldFilter | None = None,
    ) -> str:
        """Formats the dataset into markdown.

        Args:
            level (int, optional): The header level of the documentation. Defaults to 2.
            include (FieldFilter, optional): A list of conditions to require for fields to be included. Performs an OR operation.
            exclude (FieldFilter, optional): A list of conditions to exclude fields with. Performs an OR operation.

        Returns:
            str: The dataset described in markdown.
        """
        f = Formatter(self, level)
        return f.format(include=include, exclude=exclude)
