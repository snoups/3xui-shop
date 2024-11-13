import datetime
import math

from bot.utils.localization import localization
from bot.utils.logger import Logger

logger: Logger = Logger(__name__)


def convert_size(size_bytes: int, user_lang: str) -> str:
    """
    Converts a file size from bytes into a human-readable string using localized size units.

    Args:
        size_bytes (int): The size in bytes.
        user_lang (str): The user's language code.

    Returns:
        str: The size converted to the appropriate unit (KB, MB, GB, etc.).
    """
    if size_bytes == 0:
        return f"0 {localization.get_text('SIZES.BYTES', user_lang)}"
    elif size_bytes == -1:
        return f"∞"

    size_units_keys = [
        "SIZES.BYTES",
        "SIZES.KILOBYTES",
        "SIZES.MEGABYTES",
        "SIZES.GIGABYTES",
        "SIZES.TERABYTES",
        "SIZES.PETABYTES",
        "SIZES.EXABYTES",
        "SIZES.ZETTABYTES",
        "SIZES.YOTTABYTES",
    ]

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    if s.is_integer():
        s = int(s)

    size_unit = localization.get_text(size_units_keys[i], user_lang)
    return f"{s} {size_unit}"


def time_left_to_expiry(expiry_time: int, user_lang: str = "EN") -> str | int:
    """
    Calculates the time left until subscription expiry, using localized time units.

    Args:
        expiry_time (int): Expiry time as a Unix timestamp.
        user_lang (str): The user's language code.

    Returns:
        str: Time left in days, hours, and minutes or '∞' if no expiry.
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

    day_text = localization.get_text("TIME.DAY", user_lang)
    hours_text = localization.get_text("TIME.HOURS", user_lang)
    minutes_text = localization.get_text("TIME.MINUTES", user_lang)

    return f"{int(days)}{day_text}, {int(hours)}{hours_text}, {int(minutes)}{minutes_text}"
