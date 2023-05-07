"""
Extracts the data from the Oryx website.
"""
import requests
from prefect.serializers import CompressedJSONSerializer
from prefect.tasks import exponential_backoff, task

from ...utilities.blocks import task_persistence_subfolder
from .. import blocks


@task_persistence_subfolder(blocks.persistence_bucket)
@task(
    tags=["www.oryxspioenkop.com", "requests"],
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
    retry_jitter_factor=0.5,
    persist_result=True,
    # result_storage set by wrapper
    result_serializer=CompressedJSONSerializer(compressionlib="gzip"),
)
def get_russian_equipment_loss_page() -> str:
    """Requests the Russian equipment losses [web page](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html)\
    from Oryx.

    Returns
    -------
    str
        String of the page
    """
    r: requests.Response = requests.get(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html"
    )
    r.raise_for_status()
    return r.text


@task_persistence_subfolder(blocks.persistence_bucket)
@task(
    tags=["www.oryxspioenkop.com", "requests"],
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=10),
    retry_jitter_factor=0.5,
    persist_result=True,
    # result_storage set by wrapper
    result_serializer=CompressedJSONSerializer(compressionlib="gzip"),
)
def get_ukrainian_equipment_loss_page() -> str:
    """Requests the Ukrainian equipment losses [web page](https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html)\
    from Oryx.

    Returns
    -------
    str
        String of the page
    """
    r: requests.Response = requests.get(
        "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-ukrainian.html"
    )
    r.raise_for_status()
    return r.text
