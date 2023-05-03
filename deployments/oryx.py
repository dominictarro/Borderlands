"""
Deployment objects.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from prefect_github import GitHubRepository

from blocks.core import borderlands_github
from blocks.oryx import oryx_ecs_task
from flows.oryx_stage import stage_oryx_equipment_losses

oryx_deployment = Deployment.build_from_flow(
    flow=stage_oryx_equipment_losses,
    name="Semi-Daily",
    description="Deployment of the Oryx staging pipeline that runs twice a day.",
    schedule=CronSchedule(cron="0 0,12 * * *", timezone="America/New_York"),
    storage=borderlands_github,
    infrastructure=oryx_ecs_task,
    tags=["oryx"],
    work_queue_name="default",
)
