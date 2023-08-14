"""
Generate docs for the datasets.
"""
import re
from pathlib import Path

from borderlands.schema.dataset import Dataset

PROJECT_ROOT = Path(__file__).parent.parent

START_INDICATOR = "<!-- BEGIN SCHEMA SECTION -->"
END_INDICATOR = "<!-- END SCHEMA SECTION -->"
SCHEMA_SECTION_REGEX: re.Pattern = re.compile(
    (START_INDICATOR + r"(.*)" + END_INDICATOR),
    re.DOTALL | re.MULTILINE,
)


def insert_to_docs(dataset: Dataset, markdown: str) -> str:
    """Add a dataset to the markdown text.

    Args:
        markdown (str): The markdown text to insert the dataset within.

    Returns:
        str: The dataset documentation.
    """
    match: re.Match = SCHEMA_SECTION_REGEX.search(markdown)
    if match is None:
        print(markdown)
        raise ValueError("Could not find schema section in markdown.")
    return SCHEMA_SECTION_REGEX.sub(
        "\n\n".join((START_INDICATOR, dataset.to_markdown(), END_INDICATOR)),
        markdown,
    )


def update_dataset_docs(dataset: Dataset) -> str:
    """Update the dataset documentation.

    Args:
        dataset (Dataset): The dataset to update the documentation for.

    Returns:
        str: The dataset documentation.
    """
    path = PROJECT_ROOT / "docs" / f"{dataset.label}.md"
    markdown = path.read_text()
    markdown = insert_to_docs(dataset, markdown)
    path.write_text(markdown)
    print(f"Updated {dataset.label} docs.\n'{path!s}'")
