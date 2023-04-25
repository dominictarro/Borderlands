"""
Input/Output utilities/
"""
from __future__ import annotations

import json
import sys
from io import BufferedIOBase, TextIOBase
from pathlib import Path
from typing import IO, Any

from prefect import get_run_logger, task
from prefect_aws import S3Bucket


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
