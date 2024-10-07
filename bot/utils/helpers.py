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
    if size_bytes <= 0:
        return f"0 {localization.get_text('SIZES.BYTES', user_lang)}"

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


def time_left_to_expiry(expiry_time: int, user_lang: str) -> str:
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
        return localization.get_text("EXPIRED", user_lang)

    days, remainder = divmod(time_left.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    day_text = localization.get_text("TIME.DAY", user_lang)
    hours_text = localization.get_text("TIME.HOURS", user_lang)
    minutes_text = localization.get_text("TIME.MINUTES", user_lang)

    return f"{int(days)}{day_text}, {int(hours)}{hours_text}, {int(minutes)}{minutes_text}"


def calculate_remaining_traffic(current_traffic: int, max_traffic: int, lang: str) -> str:
    """
    Calculates and returns the remaining traffic as a formatted string.

    Args:
        current_traffic (int): The amount of traffic already used, in bytes.
        max_traffic (int): The maximum traffic allowed by the user's plan, in bytes.
        lang (str): The user's language code for localization.

    Returns:
        str: The remaining traffic in a human-readable format (e.g., "13.4 GB").
    """
    remaining_traffic = max_traffic - current_traffic
    return convert_size(remaining_traffic, lang)
