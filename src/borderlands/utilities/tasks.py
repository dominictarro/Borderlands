"""
Generic tasks for the Borderlands project.
"""

import json
import sys
from io import BufferedIOBase, TextIOBase
from pathlib import Path
from typing import IO, Any

import polars as pl
from prefect import task
from prefect_aws import S3Bucket
from prefecto.logging import get_prefect_or_default_logger

concat = task(pl.concat, tags=["polars"])


@task
def depaginate(pages: list[list[Any]]) -> list[Any]:
    """Depaginate a list of pages into a single list."""
    return sum(pages, [])


@task
def tabulate_s3_objects(objects: list[dict[str, Any]]) -> pl.DataFrame:
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
    return pl.from_dicts(objects)


@task
def upload(
    content: bytes | IO | Path | str | Any, key: str, bucket: S3Bucket, **kwds
) -> str:
    """Uploads the `content` under `key` to the given `bucket.`

    :param content: Object with a supported `S3Bucket` write method. Write\
        methods include:

        - `write_path` (`bytes`, `str`, or JSON-encoded object)
        - `upload_from_file_object` (IO object with `read`)
        - `upload_from_folder` (`Path` that points to a directory)
        - `upload_from_path` (`Path` that points to a non-directory)

    :param key:         Key to write `content` to
    :param bucket:      Bucket to write to
    :param cls:         `JSONEncoder` to encode non-byte/string/IO object with
    :param encoding:    `str.encode` encoding argument. Defaults to system
    :param error:       `str.encode` error argument. Defaults to 'strict'
    :return:            Full key the content was written to
    """
    logger = get_prefect_or_default_logger()
    if isinstance(content, bytes):
        logger.info("Uploading %s bytes to '%s'", len(content), key)
        # Bytes
        path = bucket.write_path(key, content)
    elif issubclass(content.__class__, (BufferedIOBase, TextIOBase)):
        # File object
        path = bucket.upload_from_file_object(content, key, **kwds)
    elif isinstance(content, Path):
        # File or folder
        if content.is_dir():
            path = bucket.upload_from_folder(content, key, **kwds)
        else:
            path = bucket.upload_from_path(content, key, **kwds)
    elif isinstance(content, str):
        # String
        encoding = kwds.get("encoding", sys.getdefaultencoding())
        errors = kwds.get("errors", "strict")
        content = content.encode(encoding, errors)
        path = upload.fn(content, key, bucket, **kwds)
    else:
        # JSON
        encoder = kwds.get("cls", json.JSONEncoder())
        content = encoder.encode(content)
        path = upload.fn(content, key, bucket, **kwds)
    return path
