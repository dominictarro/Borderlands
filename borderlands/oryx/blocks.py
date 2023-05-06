"""
Blocks for the Oryx pipeline.
"""
from ..storage import bucket
from ..utilities.blocks import create_child_bucket

oryx_bucket = create_child_bucket("oryx", "-oryx", parent=bucket, save=True)
landing_bucket = create_child_bucket(
    "landing", "-landing", parent=oryx_bucket, save=True
)
assets_bucket = create_child_bucket("assets", "-assets", parent=oryx_bucket, save=True)
persistence_bucket = create_child_bucket(
    "persistence", "-persistence", parent=oryx_bucket, save=True
)
media_bucket = create_child_bucket("media", "-media", parent=oryx_bucket, save=True)
