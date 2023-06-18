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

/*
Core datasets and releases bucket.
*/

variable "s3_bucket_core" {
    type = string
    description = "Name of the S3 bucket to store core files."
    default = "borderlands-core"
}

variable "oryx_latest_release_key" {
    type = string
    description = "Key for the latest release file."
    default = "oryx/landing/latest.json"
}

resource "aws_s3_bucket" "core_bucket" {
    bucket = var.s3_bucket_core
}

# Make public access possible
resource "aws_s3_bucket_public_access_block" "core_bucket" {
  bucket = aws_s3_bucket.core_bucket.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

# Restrict public access to read/list only
resource "aws_s3_bucket_policy" "core_bucket" {
  bucket = aws_s3_bucket.core_bucket.id
  policy = data.aws_iam_policy_document.core_bucket.json
}


data "aws_iam_policy_document" "core_bucket" {
    statement {
            principals {
                type = "*"
                identifiers = ["*"]
            }

            actions = [
                "s3:GetObject",
                "s3:ListBucket",
            ]

            resources = [
                aws_s3_bucket.core_bucket.arn,
                "${aws_s3_bucket.core_bucket.arn}/*",
            ]
    }
}


/*
Oryx media bucket.
*/

variable "s3_bucket_media" {
    type = string
    description = "Name of the S3 bucket to store media files."
    default = "borderlands-media"
    
}

resource "aws_s3_bucket" "media_bucket" {
    bucket = var.s3_bucket_media
}

resource "aws_s3_bucket_request_payment_configuration" "media_bucket" {
  bucket = aws_s3_bucket.media_bucket.id
  payer  = "Requester"
}
