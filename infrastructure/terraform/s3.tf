/*
Borderlands S3 buckets configuration.
*/

/*
Persistence bucket for Prefect.
*/

variable "s3_bucket_persistence" {
    type = string
    description = "Name of the S3 bucket to store Prefect persistence files."
    default = "borderlands-persistence"
}

resource "aws_s3_bucket" "persistence_bucket" {
    bucket = var.s3_bucket_persistence
}

resource "aws_s3_bucket_lifecycle_configuration" "persistence_bucket" {
    bucket = aws_s3_bucket.persistence_bucket.id

    rule {
        id = "Delete Old Persistence Files"
        status = "Enabled"
        noncurrent_version_expiration {
            noncurrent_days = 10
        }
    }
}

output "persistence_bucket_id" {
    value = aws_s3_bucket.persistence_bucket.id
    description = "ID of the S3 bucket to store Prefect persistence files."
}

/*
Core datasets and releases bucket.
*/

variable "s3_bucket_core" {
    type = string
    description = "Name of the S3 bucket to store Borderlands files."
    default = "borderlands-core"
}

resource "aws_s3_bucket" "core_bucket" {
    bucket = var.s3_bucket_core
}

output "core_bucket_id" {
    value = aws_s3_bucket.core_bucket.id
    description = "ID of the S3 bucket to store Borderlands files."
}