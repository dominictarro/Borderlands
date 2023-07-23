"""
Input/Output utilities/
"""
from __future__ import annotations

import mimetypes
from typing import Any

from prefect import task
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
