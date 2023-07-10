"""
Generic tasks for the Borderlands project.
"""
from typing import Any

import pandas as pd
from prefect import task

concat = task(pd.concat)


@task
def depaginate(pages: list[list[Any]]) -> list[Any]:
    """Depaginate a list of pages into a single list."""
    return sum(pages, [])


@task
def tabulate_s3_objects(objects: list[dict[str, Any]]) -> pd.DataFrame:
    """Converts a list of S3 objects into a DataFrame.

    S3 objects are dictionaries like

    ```python
    {
        "Key": "path/to/file.ext",
        "LastModified": datetime.datetime(2021, 1, 1, 0, 0, 0),
        "ETag": "abc123",
        "Size": 123,
        "StorageClass": "STANDARD",
    }
    ```
    """
    df = pd.DataFrame(
        objects,
        columns=["Key", "LastModified", "ETag", "Size", "StorageClass"],
    )
    return df
