"""
Storage blocks for the pipeline.
"""
from prefect_aws import S3Bucket
from prefecto.filesystems import create_child

core_bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands-core")
persistence_bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands-persistence")

oryx_bucket: S3Bucket = create_child(core_bucket, "oryx", "-oryx")
assets_bucket: S3Bucket = create_child(core_bucket, "assets", "-assets")
media_bucket: S3Bucket = create_child(core_bucket, "media", "-media")
