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
