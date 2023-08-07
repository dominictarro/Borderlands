"""
Oryx configuration blocks.
"""
from prefect_aws import ECSTask

try:
    from . import tf, utils
except ImportError:
    import tf
    import utils

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
                "polars",
                "prefect-github",
                "prefect-aws",
                "prefecto",
                "httpx",
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
    utils.run(utils.save(oryx_ecs_task))
