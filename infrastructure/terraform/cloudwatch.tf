/*
Creates a CloudWatch log group.
*/

resource "aws_cloudwatch_log_group" "prefect" {
    name = "prefect"
    retention_in_days = 30
}
