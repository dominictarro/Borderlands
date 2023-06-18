"""
Terraform variables.
"""

PREFECT_AGENT_EXECUTION_ROLE_ARN = (
    "arn:aws:iam::604611895840:role/prefect-agent-execution-role-borderlands-prefect"
)
PREFECT_AGENT_TASK_ROLE_ARN = (
    "arn:aws:iam::604611895840:role/prefect-agent-task-role-borderlands-prefect"
)
PREFECT_AGENT_CLUSTER_NAME = "prefect-agent-borderlands-prefect"

CORE_BUCKET_NAME = "borderlands-core"
PERSISTENCE_BUCKET_NAME = "borderlands-persistence"
MEDIA_BUCKET_NAME = "borderlands-media"
