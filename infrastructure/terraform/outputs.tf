output "prefect_agent_service_id" {
  description = "ID of the Agent's ECS Service running within the cluster"
  value = aws_ecs_service.prefect_agent_service.id
}

output "prefect_agent_execution_role_arn" {
  description = "ARN of the Agent's ECS Execution Role. Use for Prefect ECS blocks."
  value = aws_iam_role.prefect_agent_execution_role.arn
}

output "prefect_agent_task_role_arn" {
  description = "ARN of the Agent's ECS Task Role. Use for Prefect ECS blocks."
  value = var.agent_task_role_arn == null ? aws_iam_role.prefect_agent_task_role[0].arn : var.agent_task_role_arn
}

output "prefect_agent_security_group" {
  description = "ID of the Agent Service's ECS Security Group."
  value = aws_security_group.prefect_agent.id
}

output "prefect_agent_cluster_name" {
  description = "Name of the Agent Service's ECS Cluster. Use for Prefect ECS blocks."
  value = aws_ecs_cluster.prefect_agent_cluster.name
}