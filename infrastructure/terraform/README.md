# Borderlands Infrastructure

Terraform configuration for building Borderlands's execution infrastructure.

- [Borderlands Infrastructure](#borderlands-infrastructure)
  - [Requirements](#requirements)
  - [Providers](#providers)
  - [Modules](#modules)
  - [Resources](#resources)
  - [Inputs](#inputs)
  - [Outputs](#outputs)
  - [Guides](#guides)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.67.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.prefect](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_iam_policy_attachment.ecr_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy_attachment) | resource |
| [aws_iam_policy_attachment.s3_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy_attachment) | resource |
| [aws_iam_user.cicd](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_iam_user.prefect](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_user) | resource |
| [aws_s3_bucket.core_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_s3_bucket_core"></a> [s3\_bucket\_core](#input\_s3\_bucket\_core) | Name of the S3 bucket to store Borderlands files. | `string` | `"borderlands-core"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_borderlands_cicd_user_name"></a> [borderlands\_cicd\_user\_name](#output\_borderlands\_cicd\_user\_name) | Name of the Borderlands CI/CD AWS user. |
| <a name="output_core_bucket_id"></a> [core\_bucket\_id](#output\_core\_bucket\_id) | ID of the S3 bucket to store Borderlands files. |
| <a name="output_prefect_user_name"></a> [prefect\_user\_name](#output\_prefect\_user\_name) | Name of the Prefect AWS user. |
<!-- END_TF_DOCS -->

## Guides

- [Terraforming AWS Networks](https://medium.com/appgambit/terraform-aws-vpc-with-private-public-subnets-with-nat-4094ad2ab331)
