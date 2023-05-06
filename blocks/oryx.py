"""
Oryx configuration blocks.
"""
from prefect_aws import ECSTask

try:
    from . import tf
except ImportError:
    import tf

oryx_ecs_task: ECSTask = ECSTask(
    name="ecs-task-oryx",
    image="prefecthq/prefect:2-python3.11",
    cpu=512,
    memory=1024,
    env={
        "EXTRA_PIP_PACKAGES": " ".join(
            (
                "beautifulsoup4",
                "lxml",
                "marshmallow",
                "pandas",
                "prefect-github",
                "prefect-aws",
                "requests",
                "tabulate",
            )
        ),
    },
    configure_cloudwatch_logs=True,
    cloudwatch_logs_options={
        "awslogs-stream-prefix": "Oryx",
    },
    # AWS infrastructure
    execution_role_arn=tf.PREFECT_AGENT_EXECUTION_ROLE_ARN,
    task_role_arn=tf.PREFECT_AGENT_TASK_ROLE_ARN,
    cluster=tf.PREFECT_AGENT_CLUSTER_NAME,
    _block_document_name="ecs-task-oryx",
)

if __name__ == "__main__":
    oryx_ecs_task.save(name=oryx_ecs_task._block_document_name, overwrite=True)
