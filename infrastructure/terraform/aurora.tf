
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

// ------------------------------
// RDS Cluster

resource "aws_rds_cluster" "borderlands_prod" {
    // Cluster config
    cluster_identifier = "borderlands-prod"
    engine = "aurora-mysql"
    engine_version = "8.0.mysql_aurora.3.02.0"

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
    backtrack_window = 7
    apply_immediately = true
    skip_final_snapshot = true

    // Network
    vpc_security_group_ids = var.security_group_ids
    network_type = "IPV4"

    // Logs
    enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]

    tags = {
        project = "borderlands"
    }
}

output "rds_cluster_endpoint" {
    description = "The endpoint of the RDS cluster."
    value = aws_rds_cluster.borderlands_prod.endpoint  
}

output "rds_cluster_reader_endpoint" {
    description = "The reader endpoint of the RDS cluster."
    value = aws_rds_cluster.borderlands_prod.reader_endpoint
}

output "rds_hosted_zone_id" {
    description = "The hosted zone ID of the RDS cluster."
    value = aws_rds_cluster.borderlands_prod.hosted_zone_id
}
