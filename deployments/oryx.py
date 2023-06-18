"""
Deployment objects.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

from blocks.core import borderlands_github
from blocks.oryx import oryx_ecs_task
from flows.oryx_media import extract_oryx_media
from flows.oryx_stage import stage_oryx_equipment_losses

oryx_deployment: Deployment = Deployment.build_from_flow(
    flow=stage_oryx_equipment_losses,
    name="Daily",
    description="Deployment of the Oryx staging pipeline that runs daily.",
    schedule=CronSchedule(cron="0 0 * * *", timezone="America/New_York"),
    storage=borderlands_github,
    infrastructure=oryx_ecs_task,
    tags=["oryx"],
    work_queue_name="default",
)

oryx_media_deployment: Deployment = Deployment.build_from_flow(
    flow=extract_oryx_media,
    name="Trigger",
    description="Deployment of the Oryx media extraction pipeline that runs on demand.",
    storage=borderlands_github,
    infrastructure=oryx_ecs_task,
    tags=["oryx", "trigger"],
    work_queue_name="default",
)
