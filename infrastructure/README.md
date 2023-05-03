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
| <a name="provider_aws"></a> [aws](#provider\_aws) | 4.64.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_log_group.prefect_agent_log_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_ecs_cluster.prefect_agent_cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_cluster) | resource |
| [aws_ecs_cluster_capacity_providers.prefect_agent_cluster_capacity_providers](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_cluster_capacity_providers) | resource |
| [aws_ecs_service.prefect_agent_service](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_service) | resource |
| [aws_ecs_task_definition.prefect_agent_task_definition](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition) | resource |
| [aws_iam_role.prefect_agent_execution_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.prefect_agent_task_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_internet_gateway.borderlands_igw](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway) | resource |
| [aws_route_table.borderlands_public_rt](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table) | resource |
| [aws_route_table_association.borderlands_public_subnet_rt_association](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association) | resource |
| [aws_secretsmanager_secret.prefect_api_key](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.prefect_api_key_version](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [aws_security_group.prefect_agent](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_security_group_rule.https_outbound](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group_rule) | resource |
| [aws_subnet.borderlands_private_subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_subnet.borderlands_public_subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_vpc.borderlands_vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc) | resource |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_agent_cpu"></a> [agent\_cpu](#input\_agent\_cpu) | CPU units to allocate to the agent | `number` | `256` | no |
| <a name="input_agent_desired_count"></a> [agent\_desired\_count](#input\_agent\_desired\_count) | Number of agents to run | `number` | `1` | no |
| <a name="input_agent_extra_pip_packages"></a> [agent\_extra\_pip\_packages](#input\_agent\_extra\_pip\_packages) | Packages to install on the agent assuming image is based on prefecthq/prefect | `string` | `"prefect-aws prefect-github"` | no |
| <a name="input_agent_image"></a> [agent\_image](#input\_agent\_image) | Container image for the agent. This could be the name of an image in a public repo or an ECR ARN | `string` | `"prefecthq/prefect:2-python3.11"` | no |
| <a name="input_agent_log_retention_in_days"></a> [agent\_log\_retention\_in\_days](#input\_agent\_log\_retention\_in\_days) | Number of days to retain agent logs for | `number` | `30` | no |
| <a name="input_agent_memory"></a> [agent\_memory](#input\_agent\_memory) | Memory units to allocate to the agent | `number` | `512` | no |
| <a name="input_agent_queue_name"></a> [agent\_queue\_name](#input\_agent\_queue\_name) | Prefect queue that the agent should listen to | `string` | `"default"` | no |
| <a name="input_agent_task_role_arn"></a> [agent\_task\_role\_arn](#input\_agent\_task\_role\_arn) | Optional task role ARN to pass to the agent. If not defined, a task role will be created | `string` | `null` | no |
| <a name="input_name"></a> [name](#input\_name) | Unique name for this agent deployment | `string` | n/a | yes |
| <a name="input_prefect_account_id"></a> [prefect\_account\_id](#input\_prefect\_account\_id) | Prefect cloud account ID | `string` | n/a | yes |
| <a name="input_prefect_api_key"></a> [prefect\_api\_key](#input\_prefect\_api\_key) | Prefect cloud API key | `string` | n/a | yes |
| <a name="input_prefect_workspace_id"></a> [prefect\_workspace\_id](#input\_prefect\_workspace\_id) | Prefect cloud workspace ID | `string` | n/a | yes |
| <a name="input_secrets_manager_recovery_in_days"></a> [secrets\_manager\_recovery\_in\_days](#input\_secrets\_manager\_recovery\_in\_days) | Deletion delay for AWS Secrets Manager upon resource destruction | `number` | `30` | no |
| <a name="input_vpc_availability_zone"></a> [vpc\_availability\_zone](#input\_vpc\_availability\_zone) | Availability zone for the VPC. | `string` | `"us-east-1a"` | no |
| <a name="input_vpc_cidr_block"></a> [vpc\_cidr\_block](#input\_vpc\_cidr\_block) | CIDR for the VPC. | `string` | `"10.0.0.0/16"` | no |
| <a name="input_vpc_private_subnet_cidr_block"></a> [vpc\_private\_subnet\_cidr\_block](#input\_vpc\_private\_subnet\_cidr\_block) | CIDR for the private subnet. | `string` | `"10.0.2.0/24"` | no |
| <a name="input_vpc_public_subnet_cidr_block"></a> [vpc\_public\_subnet\_cidr\_block](#input\_vpc\_public\_subnet\_cidr\_block) | CIDR for the public subnet. | `string` | `"10.0.1.0/24"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_borderlands_vpc_id"></a> [borderlands\_vpc\_id](#output\_borderlands\_vpc\_id) | VPC ID for Borderlands AWS infrastructure. |
| <a name="output_prefect_agent_cluster_name"></a> [prefect\_agent\_cluster\_name](#output\_prefect\_agent\_cluster\_name) | Name of the Agent Service's ECS Cluster. Use for Prefect ECS blocks. |
| <a name="output_prefect_agent_execution_role_arn"></a> [prefect\_agent\_execution\_role\_arn](#output\_prefect\_agent\_execution\_role\_arn) | ARN of the Agent's ECS Execution Role. Use for Prefect ECS blocks. |
| <a name="output_prefect_agent_security_group"></a> [prefect\_agent\_security\_group](#output\_prefect\_agent\_security\_group) | ID of the Agent Service's ECS Security Group. |
| <a name="output_prefect_agent_service_id"></a> [prefect\_agent\_service\_id](#output\_prefect\_agent\_service\_id) | ID of the Agent's ECS Service running within the cluster |
| <a name="output_prefect_agent_task_role_arn"></a> [prefect\_agent\_task\_role\_arn](#output\_prefect\_agent\_task\_role\_arn) | ARN of the Agent's ECS Task Role. Use for Prefect ECS blocks. |
<!-- END_TF_DOCS -->

## Guides

- [Terraforming AWS Networks](https://medium.com/appgambit/terraform-aws-vpc-with-private-public-subnets-with-nat-4094ad2ab331)
