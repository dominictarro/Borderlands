"""
Storage blocks for the pipeline.
"""
from prefect_aws import S3Bucket
from prefecto.filesystems import create_child

core_bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands-core")
persistence_bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands-persistence")
media_bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands-media")

landing_bucket = create_child(core_bucket, "landing", "-landing")
assets_bucket = create_child(core_bucket, "assets", "-assets")
