/*
Borderlands AWS users.

*/

resource "aws_iam_user" "prefect" {
    name = "Prefect"
}

resource "aws_iam_policy_attachment" "s3_access" {
    name = "S3Access"
    policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    users = [
        aws_iam_user.prefect.name
    ]
}

output "prefect_user_name" {
    value = aws_iam_user.prefect.name
    description = "Name of the Prefect AWS user."
}

# User for CI/CD

resource "aws_iam_user" "cicd" {
    name = "BorderlandsCICD"
}

resource "aws_iam_policy_attachment" "ecr_access" {
    name = "ECRAccess"
    policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
    users = [
        aws_iam_user.cicd.name
    ]
}

output "borderlands_cicd_user_name" {
    value = aws_iam_user.cicd.name
    description = "Name of the Borderlands CI/CD AWS user."
}