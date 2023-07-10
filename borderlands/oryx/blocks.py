"""
Blocks for the Oryx pipeline.
"""
from prefecto.filesystems import create_child

from ..storage import bucket, media_bucket, persistence_bucket

oryx_bucket = bucket
landing_bucket = create_child(bucket, "landing", "-landing")
assets_bucket = create_child(bucket, "assets", "-assets")
persistence_bucket = persistence_bucket
media_bucket = media_bucket
