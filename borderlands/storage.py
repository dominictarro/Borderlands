"""
Storage blocks for the pipeline.
"""
from prefect_aws import S3Bucket

bucket: S3Bucket = S3Bucket.load("s3-bucket-borderlands")
