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
| [aws_s3_bucket.core_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket.persistence_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_bucket_lifecycle_configuration.persistence_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration) | resource |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_s3_bucket_core"></a> [s3\_bucket\_core](#input\_s3\_bucket\_core) | Name of the S3 bucket to store Borderlands files. | `string` | `"borderlands-core"` | no |
| <a name="input_s3_bucket_persistence"></a> [s3\_bucket\_persistence](#input\_s3\_bucket\_persistence) | Name of the S3 bucket to store Prefect persistence files. | `string` | `"borderlands-persistence"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_core_bucket_id"></a> [core\_bucket\_id](#output\_core\_bucket\_id) | ID of the S3 bucket to store Borderlands files. |
| <a name="output_persistence_bucket_id"></a> [persistence\_bucket\_id](#output\_persistence\_bucket\_id) | ID of the S3 bucket to store Prefect persistence files. |
<!-- END_TF_DOCS -->

## Guides

- [Terraforming AWS Networks](https://medium.com/appgambit/terraform-aws-vpc-with-private-public-subnets-with-nat-4094ad2ab331)
