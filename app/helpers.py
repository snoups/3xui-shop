import datetime
import logging
import math

from aiogram.utils.i18n import gettext as _
from py3xui import Client

logger = logging.getLogger(__name__)


def parse_client_data(client: Client) -> dict | None:
    """
    Parse and structure client data retrieved from the XUI API.

    Args:
        client (Client): The client object containing data from the XUI API.

    Returns:
        dict | None: A dictionary with structured client data, including:
                     - "plan": Total traffic plan in bytes.
                     - "remaining_traffic": Remaining traffic in bytes.
                     - "expiry_time": Expiry time as a Unix timestamp.
                     - "total": Total traffic used in bytes.
                     - "up": Uploaded traffic in bytes.
                     - "down": Downloaded traffic in bytes.
                     Returns `None` if the client object is invalid.
    """
    try:
        if client is None:
            return None

        logger.debug(client.model_dump())

        if client.total == 0:
            remaining_traffic = -1
            plan = -1
        else:
            remaining_traffic = client.total - (client.up + client.down)
            plan = client.total

        total = client.up + client.down
        up = client.up
        down = client.down
        expiry_time = client.expiry_time

        return {
            "plan": plan,
            "remaining_traffic": remaining_traffic,
            "expiry_time": expiry_time,
            "total": total,
            "up": up,
            "down": down,
        }
    except Exception as e:
        logger.error(f"Error processing client data for {client.email}: {e}")
        return {}


def convert_size(size_bytes: int) -> str:
    """
    Convert a file size from bytes to a human-readable format.

    Args:
        size_bytes (int): Size in bytes.

    Returns:
        str: The formatted size with appropriate units (e.g., KB, MB, GB).
              Returns '∞' if size_bytes is -1.
    """
    if size_bytes == 0:
        return f"0 {_('B')}"
    elif size_bytes == -1:
        return "∞"

    size_units_keys = [
        _("B"),
        _("KB"),
        _("MB"),
        _("GB"),
        _("TB"),
        _("PB"),
        _("EB"),
        _("ZB"),
        _("YB"),
    ]

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    if s.is_integer():
        s = int(s)

    size_unit = size_units_keys[i]
    return f"{s} {size_unit}"


def time_left_to_expiry(expiry_time: int) -> str | int:
    """
    Calculate the time remaining until a subscription expires.

    Args:
        expiry_time (int): Expiry time as a Unix timestamp in milliseconds.

    Returns:
        str | int: A formatted string with the time left (e.g., '2d, 3h, 15m'),
                   '∞' if no expiry time is set, or -1 if the subscription has already expired.
    """
    if expiry_time == 0:
        return "∞"

    now = datetime.datetime.now()
    expiry_datetime = datetime.datetime.fromtimestamp(expiry_time / 1000)

    time_left = expiry_datetime - now
    if time_left.total_seconds() < 0:
        return -1

    days, remainder = divmod(time_left.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    return f"{int(days)}{_('d')}, {int(hours)}{_('h')}, {int(minutes)}{_('m')}"
