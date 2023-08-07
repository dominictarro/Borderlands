"""
Flow to release the Borderlands dataset to Kaggle.
"""
import datetime
import enum
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path

import polars as pl
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect.context import get_run_context
from prefect.utilities.asyncutils import sync_compatible

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except OSError:
    from kaggle.api.kaggle_api_extended import KaggleApi

from kaggle.rest import ApiException

from borderlands.definitions import oryx
from borderlands.schema import Dataset, Field, Tag
from borderlands.schema.schema import FieldFilter

__project__ = Path(__file__).parent.parent


class DatasetStatus(enum.Enum):
    """The status of a dataset."""

    EXISTS = enum.auto()
    DOES_NOT_EXIST = enum.auto()


@sync_compatible
async def get_kaggle_authentication_config() -> dict:
    """Get the Kaggle authentication config."""
    return {
        "username": (await Secret.load("secret-kaggle-username")).get(),
        "key": (await Secret.load("secret-kaggle-key")).get(),
    }


def get_dataset_metadata() -> dict:
    """Get the dataset metadata."""
    with open(__project__ / "kaggle" / "dataset-metadata.json", "r") as f:
        return json.load(f)


def get_kaggle_client() -> KaggleApi:
    """Get a Kaggle API client."""
    api = KaggleApi()
    api._load_config(get_kaggle_authentication_config())
    return api


def update_description(metadata: dict) -> dict:
    """Updates the description in the dataset metadata file.

    Args:
        metadata (dict): The dataset metadata.

    Returns:
        dict: The updated dataset metadata.
    """
    with open(__project__ / "kaggle" / "README.md", "r") as f:
        metadata["description"] = f.read()
    return metadata


def assess_dataset_status(api: KaggleApi, metadata: dict) -> DatasetStatus:
    """Assess the status of the dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.

    Returns:
        DatasetStatus: The status of the dataset.
    """
    try:
        # Dataset exists, create new version
        api.dataset_status(metadata["id"])
        return DatasetStatus.EXISTS
    except ApiException as e:
        if e.reason == "Forbidden" and e.status == 403:
            return DatasetStatus.DOES_NOT_EXIST
        raise e


def stage_dataset_as_json(
    dataset: Dataset,
    folder: str | Path,
    include: FieldFilter | None = None,
    exclude: FieldFilter | None = None,
) -> Path:
    """Stage a dataset as JSON records.

    Args:
        dataset (Dataset): The dataset to stage.
        folder (str | Path): The folder to stage the dataset to.
        include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
        exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

    Returns:
        Path: The path to the staged dataset.
    """
    df = dataset.read(include, exclude)
    path = Path(folder) / f"{dataset.label}.json"
    df.write_json(path, row_oriented=True)
    return path


def create_kaggle_type(dtype: pl.DataType) -> str:
    """Create a Kaggle type from a Polars type.

    Args:
        dtype (pl.DataType): The Polars type.

    Returns:
        str: The Kaggle type.
    """
    if dtype in (
        pl.Decimal,
        pl.Float32,
        pl.Float64,
        pl.Int8,
        pl.Int16,
        pl.Int32,
        pl.Int64,
        pl.UInt8,
        pl.UInt16,
        pl.UInt32,
        pl.UInt64,
    ):
        return "numeric"
    elif dtype == pl.Boolean:
        return "boolean"
    elif dtype in (pl.Categorical, pl.Date, pl.Duration, pl.Time, pl.Utf8):
        return "string"
    elif dtype == pl.Datetime:
        return "datetime"
    elif isinstance(dtype, pl.List):
        return f"list({create_kaggle_type(dtype.inner)})"
    elif isinstance(dtype, pl.Struct):
        return f"struct({', '.join([f'{field.name}: {create_kaggle_type(field.dtype)}' for field in dtype.fields])})"
    else:
        raise ValueError(f"Unknown Polars type {dtype}")


def create_resource_column(field: Field) -> dict:
    """Create a resource column from a field.

    Args:
        field (Field): The field to create a resource column from.

    Returns:
        dict: The resource column.
    """
    return {
        "name": field.name,
        "type": create_kaggle_type(field.dtype),
        "description": field.description,
    }


def create_resource_from_dataset(
    dataset: Dataset,
    include: FieldFilter | None = None,
    exclude: FieldFilter | None = None,
) -> dict:
    """Create a resource from a dataset.

    Args:
        dataset (Dataset): The dataset to create a resource from.
        include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
        exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

    Returns:
        dict: The resource.
    """
    return {
        "path": f"{dataset.label}.json",
        "description": dataset.description,
        "schema": {
            "fields": [
                create_resource_column(field)
                for field in dataset.schema.iter(include, exclude)
            ]
        },
    }


def add_dataset(
    folder: str,
    dataset: Dataset,
    metadata: dict,
    include: FieldFilter | None = None,
    exclude: FieldFilter | None = None,
) -> Dataset:
    """Add a dataset to the catalog.

    Args:
        folder (str): The folder to stage the dataset to.
        dataset (Dataset): The dataset to add.
        metadata (dict): The dataset metadata.
        include (TagSet, optional): A list of tags to include. Defaults to None (no inclusion requirement).
        exclude (TagSet, optional): A list of tags to exclude. Defaults to None (no exclusion filter).

    """
    stage_dataset_as_json(dataset, folder, include=include, exclude=exclude)
    metadata["resources"].append(
        create_resource_from_dataset(dataset, include=include, exclude=exclude)
    )


@contextmanager
def staged_datasets_as_json(metadata: dict):
    """Stage a list of datasets as JSON records.

    Args:
        metadata (dict): The dataset metadata.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        metadata["resources"] = metadata.get("resources", [])

        # Add the datasets and add their documentation
        add_dataset(tmpdir, oryx, metadata, exclude=[Tag.metadata, Tag.debug])

        # Add the metadata file
        with open(Path(tmpdir) / "dataset-metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        try:
            yield tmpdir
        finally:
            pass


@task
def create_kaggle_dataset(api: KaggleApi, metadata: dict):
    """Create a new dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.
    """
    with staged_datasets_as_json(metadata) as tmpdir:
        api.dataset_create_new(
            tmpdir, public=metadata["isPrivate"] is False, quiet=False
        )


@task
def update_kaggle_dataset(api: KaggleApi, metadata: dict, date: datetime.date):
    """Update the dataset.

    Args:
        api (KaggleApi): The Kaggle API client.
        metadata (dict): The dataset metadata.
        date (datetime.date): The date of the release.

    """
    with staged_datasets_as_json(metadata) as tmpdir:
        api.dataset_create_version(
            tmpdir,
            version_notes=f"{date.strftime(r'%Y-%m-%d')} Release",
            quiet=False,
            delete_old_versions=True,
        )


@flow(
    name="Release Dataset to Kaggle",
    log_prints=True,
)
def release_dataset_to_kaggle():
    """Make the Kaggle dataset."""
    api = get_kaggle_client()
    metadata = get_dataset_metadata()
    metadata = update_description(metadata)
    status = assess_dataset_status(api, metadata)

    if status == DatasetStatus.DOES_NOT_EXIST:
        create_kaggle_dataset(api, metadata)
    elif status == DatasetStatus.EXISTS:
        update_kaggle_dataset(
            api, metadata, get_run_context().flow_run.expected_start_time.date()
        )
    else:
        raise ValueError(f"Unknown dataset status {status}")
