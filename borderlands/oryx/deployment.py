"""
Deployment objects.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from prefect_aws import ECSTask
from prefect_github import GitHubRepository

from .flows import stage_oryx_equipment_losses

oryx_deployment = Deployment.build_from_flow(
    flow=stage_oryx_equipment_losses,
    name="Semi-Daily",
    description="Deployment of the Oryx pipeline running twice a day.",
    schedule=CronSchedule(cron="0 0,12 * * *", timezone="America/New_York"),
    storage=GitHubRepository.load("github-repository-borderlands"),
    infrastructure=ECSTask.load("ecs-task-oryx"),
    tags=["oryx"],
    work_queue_name="default",
)
