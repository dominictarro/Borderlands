
variable "security_group_ids" {
    description = "The security group IDs for the RDS cluster."
    type        = list(string)
}

// ------------------------------
// IAM Role and Policy

resource "aws_iam_role" "rds" {
    name = "rds-iam-role"
    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Action = "sts:AssumeRole",
                Effect = "Allow",
                Principal = {
                    Service = "rds.amazonaws.com"
                }
            }
        ]
    })
    tags = {
        project = "borderlands"
    }
}

data "aws_iam_policy_document" "s3_read" {
  statement {
    effect    = "Allow"
    actions   = [
        "s3:GetObject"
    ]
    resources = [
        "${aws_s3_bucket.core_bucket.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "rds_s3_read" {
    name        = "rds-s3-read"
    description = "Allows RDS to read from S3"
    policy      = data.aws_iam_policy_document.s3_read.json
}

resource "aws_iam_role_policy_attachment" "rds_s3_read" {
    policy_arn = aws_iam_policy.rds_s3_read.arn
    role       = aws_iam_role.rds.name
}

// ------------------------------
// RDS Cluster

resource "aws_rds_cluster" "borderlands_dev" {
    // Cluster config
    cluster_identifier = "borderlands-dev"
    engine = "aurora-mysql"
    engine_mode = "provisioned"
    engine_version = "8.0.mysql_aurora.3.04.1"

    serverlessv2_scaling_configuration {
        max_capacity = 1.0
        min_capacity = 0.5
    }

    // DB instance
    database_name = "borderlands"

    // Authentication
    master_username = "admin"
    manage_master_user_password = true
    iam_database_authentication_enabled = true

    // Cluster IAM
    iam_roles = [
        "arn:aws:iam::604611895840:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
        aws_iam_role.rds.arn
    ]

    // Cluster maintenance
    apply_immediately = true
    skip_final_snapshot = true
    copy_tags_to_snapshot = true

    // Network
    vpc_security_group_ids = var.security_group_ids
    network_type = "IPV4"

    tags = {
        project = "borderlands"
    }
}

resource "aws_rds_cluster_instance" "instance_1" {
    cluster_identifier = aws_rds_cluster.borderlands_dev.cluster_identifier
    identifier = "borderlands-dev-instance-1"
    instance_class = "db.serverless"
    engine = "aurora-mysql"
    engine_version = "8.0.mysql_aurora.3.04.1"

    // Config
    promotion_tier = 1

    // Network
    publicly_accessible = true

    tags = {
        project = "borderlands"
    }
}

// ------------------------------
// RDS IAM user permissions

data "aws_iam_policy_document" "dev_rds_access" {
    statement {
        actions = [
            "rds-db:connect"
        ]
        effect = "Allow"
        // This is a distinct ARN purely for granting IAM users authentication permissions with the cluster
        resources = [
            "arn:aws:rds-db:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:dbuser:${aws_rds_cluster.borderlands_dev.cluster_resource_id}/${aws_iam_user.prefect.name}"
        ]
    }
}

resource "aws_iam_user_policy" "prefect_user_dev_rds_access" {
    name   = "dev-rds-access"
    user   = aws_iam_user.prefect.name
    policy = data.aws_iam_policy_document.dev_rds_access.json
}


// ------------------------------
// RDS Cluster Outputs

output "rds_cluster_endpoint" {
    description = "The endpoint of the RDS cluster."
    value = aws_rds_cluster.borderlands_dev.endpoint  
}

output "rds_cluster_reader_endpoint" {
    description = "The reader endpoint of the RDS cluster."
    value = aws_rds_cluster.borderlands_dev.reader_endpoint
}

output "rds_hosted_zone_id" {
    description = "The hosted zone ID of the RDS cluster."
    value = aws_rds_cluster.borderlands_dev.hosted_zone_id
}
