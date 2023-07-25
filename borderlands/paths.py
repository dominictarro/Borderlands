""""""
import datetime

from .utilities import misc


def create_oryx_key(dt: datetime.datetime | None = None, ext: str | None = None) -> str:
    """Creates the key for the Oryx equipment losses on this date.

    Args:
        dt (datetime.datetime, optional): The date the data was collected. 'latest' will be used if None. Defaults to None.
        ext (str, optional): The file extension. Defaults to None.

    """
    prefix: str = ""
    if dt is None:
        prefix = "latest"
    else:
        prefix = misc.build_datetime_key(dt, "month") + "/" + dt.strftime(r"%Y-%m-%d")
    return prefix + (f".{ext.lstrip('.')}" if ext else "")
