/*
Borderlands S3 buckets configuration.
*/

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