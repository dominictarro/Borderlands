"""
Generate docs for the datasets.
"""

import re
from pathlib import Path

import click

from borderlands.definitions import media_inventory as media_inventory_ds
from borderlands.definitions import oryx as oryx_ds
from borderlands.schema.dataset import Dataset

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

START_INDICATOR = "<!-- BEGIN SCHEMA SECTION -->"
END_INDICATOR = "<!-- END SCHEMA SECTION -->"
SCHEMA_SECTION_REGEX: re.Pattern = re.compile(
    (START_INDICATOR + r"(.*)" + END_INDICATOR),
    re.DOTALL | re.MULTILINE,
)


@click.group()
def docs():
    """Commands for working with documentation."""
    pass


def insert_to_docs(dataset: Dataset, markdown: str) -> str:
    """Add a dataset's schema to the markdown text.

    Args:
        markdown (str): The markdown text to insert the dataset within.

    Returns:
        str: The dataset documentation.
    """
    match: re.Match = SCHEMA_SECTION_REGEX.search(markdown)
    if match is None:
        raise ValueError("Could not find schema section in markdown.")
    return SCHEMA_SECTION_REGEX.sub(
        "\n\n".join((START_INDICATOR, dataset._format_schema(), END_INDICATOR)),
        markdown,
    )


def update_dataset_docs(dataset: Dataset, path: Path) -> str:
    """Update the dataset documentation.

    Args:
        dataset (Dataset): The dataset to update the documentation for.

    Returns:
        str: The dataset documentation.
    """
    markdown = path.read_text()
    markdown = insert_to_docs(dataset, markdown)
    path.write_text(markdown)
    click.echo(f"Updated {dataset.label} docs.\n'{path!s}'")


@docs.command()
@click.option(
    "-p",
    "--path",
    default=PROJECT_ROOT / "docs" / "Datasets" / "Oryx.md",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
    help="Path to the dataset.",
)
def oryx(path: Path):
    """Update the Oryx dataset documentation."""
    update_dataset_docs(oryx_ds, path)


@docs.command()
@click.option(
    "-p",
    "--path",
    default=PROJECT_ROOT / "docs" / "Datasets" / "Media Inventory.md",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
    help="Path to the dataset.",
)
def media_inventory(path: Path):
    """Update the Media Inventory dataset documentation."""
    update_dataset_docs(media_inventory_ds, path)
