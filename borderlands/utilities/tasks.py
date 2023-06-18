"""
Generic tasks for the Borderlands project.
"""
from typing import Any

import pandas as pd
from prefect import states, task
from prefect.futures import PrefectFuture
from prefect.tasks import Task

from ..utilities.loggers import get_prefect_or_default_logger

concat = task(pd.concat)


def batch(batch_size: int, **kwds) -> list[dict[str, Any]]:
    """Break the keyword iterables into batches of a given size.

    >>> batch(2, a=[1,2,3,4,5], b=[2,3,4,5,6])
    [
        {"a": [1,2], "b": [2,3]},
        {"a": [3,4], "b": [4,5]},
        {"a": [5], "b": [6]}
    ]
    """
    parameters = sorted(kwds.keys())
    if len(parameters) == 0:
        raise ValueError("Must provide at least one iterable.")

    # Validate all are iterables
    for k in parameters:
        if not hasattr(kwds[k], "__iter__"):
            raise ValueError(f"Expected '{k}' to be an iterable.")

    length = len(kwds[parameters[0]])

    # Validate all of equal length
    if len(parameters) > 1:
        for k in parameters[1:]:
            if not len(kwds[k]) == length:
                raise ValueError(
                    f"Expected all iterables to be of length {length} like '{parameters[0]}'. '{k}' is length {len(kwds[k])}."
                )

    batches = []
    current_batch = {p: [] for p in parameters}

    i = 0
    for i in range(length):
        for p in parameters:
            current_batch[p].append(kwds[p][i])

        if (i + 1) % batch_size == 0:
            batches.append(current_batch)
            current_batch = {p: [] for p in parameters}

    if (i + 1) % batch_size != 0:
        # Final update
        batches.append(current_batch)

    return batches


def batch_map(task: Task, batches: list[dict[str, Any]]) -> list[Any]:
    """Execute a task for each batch in batches."""
    logger = get_prefect_or_default_logger()
    results = []
    for i, b in enumerate(batches):
        logger.info(f"{task.name} | Starting batch {i+1} of {len(batches)}.")
        futures = task.map(**b)
        results.append(futures)

        # Poll futures to ensure they are not active.
        is_complete: bool = False
        while not is_complete:
            logger.info(f"{task.name} | Polling futures...")
            is_complete = True
            for f in futures:
                f: PrefectFuture
                if f.get_state() in (
                    states.Running,
                    states.Pending,
                    states.Retrying,
                    states.AwaitingRetry,
                ):
                    is_complete = False
                    break
            else:
                break
            # Quick and dirty way to sleep without blocking the event loop.
            f.wait(0.25)

        logger.info(f"{task.name} | Batch {i+1} of {len(batches)} complete.")

    return depaginate(results)


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
