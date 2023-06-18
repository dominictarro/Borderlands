"""
Input/Output utilities/
"""
from __future__ import annotations

import json
import mimetypes
import sys
from io import BufferedIOBase, TextIOBase
from pathlib import Path
from typing import IO, Any

from prefect import get_run_logger, task
from prefect_aws import S3Bucket


@task
def list_bucket(bucket: S3Bucket, **kwds) -> list[dict[str, Any]]:
    """Lists the contents of a bucket.

    Parameters
    ----------
    bucket : S3Bucket

    Returns
    ----------
    list[str]
    List of boto3 objects.

    Examples
    ----------

    >>> list_bucket.fn(bucket)
    [
        {
            'Key': 'oryx/landing/ukraine_2023-05-03T16-01-27.818963+00-00.json',
            'LastModified': datetime.datetime(2023, 5, 3, 16, 1, 48, tzinfo=tzutc()),
            'ETag': '"5fdcc3e411db95570a20143d431130c9"',
            'Size': 1799409,
            'StorageClass': 'STANDARD'
        }
    ]

    """
    return bucket.list_objects(**kwds)


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
    if isinstance(content, bytes):
        get_run_logger().warning("Uploading %s bytes to '%s'", len(content), key)
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


def infer_media_extension(
    url: str | None = None, headers: dict | None = None
) -> str | None:
    """Infers the best media extension give request headers and the URL."""
    mtype: str | None = None

    if headers is not None:
        if "Content-Type" in headers:
            mtype = headers["Content-Type"]

    if mtype is None:
        if url is not None:
            mtype = mimetypes.guess_type(url)[0]

    if mtype is not None:
        return mimetypes.guess_extension(mtype)
