"""
Blocks for the Oryx pipeline.
"""
from ..storage import bucket, media_bucket, persistence_bucket
from ..utilities.blocks import create_child_bucket

oryx_bucket = bucket
landing_bucket = create_child_bucket("landing", "-landing", parent=bucket, save=True)
assets_bucket = create_child_bucket("assets", "-assets", parent=bucket, save=True)
persistence_bucket = persistence_bucket
media_bucket = media_bucket
