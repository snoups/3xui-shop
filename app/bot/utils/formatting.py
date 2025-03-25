import logging
import math
from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal

from aiogram.utils.i18n import gettext as _

from app.bot.utils.constants import UNLIMITED

logger = logging.getLogger(__name__)


def format_size(size_bytes: int) -> str:
    try:
        if size_bytes == -1:
            return UNLIMITED
        if size_bytes == 0:
            return f"0 {_('MB')}"

        size_units = [_("MB"), _("GB"), _("TB"), _("PB"), _("EB"), _("ZB"), _("YB")]
        size_in_mb = max(size_bytes / 1024**2, 1)
        i = min(int(math.log(size_in_mb, 1024)), len(size_units) - 1)
        s = round(size_in_mb / (1024**i), 2)

        return f"{int(s) if s.is_integer() else s} {size_units[i]}"
    except Exception as exception:
        logger.error(f"Error converting size: {exception}")
        return f"0 {_('MB')}"


def format_remaining_time(timestamp: int) -> str:
    try:
        if timestamp == -1:
            return UNLIMITED

        now = datetime.now(timezone.utc)
        expiry_datetime = datetime.fromtimestamp(timestamp / 1000, timezone.utc)
        time_left = expiry_datetime - now

        days, remainder = divmod(time_left.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        parts = []
        if days > 0:
            parts.append(f"{int(days)}{_('d')}")
        if hours > 0:
            parts.append(f"{int(hours)}{_('h')}")
        if minutes > 0 or not parts:
            parts.append(f"{int(minutes)}{_('m')}")

        return " ".join(parts)
    except Exception as exception:
        logger.error(f"Error calculating time to expiry: {exception}")
        return f"0{_('m')}"


def format_device_count(devices: int) -> str:
    return (
        UNLIMITED + _("devices")
        if devices == -1
        else _("1 device", "{} devices", devices).format(devices)
    )


def format_subscription_period(days: int) -> str:
    if days == -1:
        return UNLIMITED
    if days % 365 == 0 and days != 0:
        return _("1 year", "{} years", days // 365).format(days // 365)
    if days % 30 == 0 and days != 0:
        return _("1 month", "{} months", days // 30).format(days // 30)
    return _("1 day", "{} days", days).format(days)


def to_decimal(amount: float | str | Decimal | int) -> Decimal:
    DECIMAL_SCALE = 18
    DECIMAL_FORMAT = f"1.{'0' * DECIMAL_SCALE}"

    if isinstance(amount, Decimal):
        result = amount
    else:
        result = Decimal(str(amount))

    return result.quantize(Decimal(DECIMAL_FORMAT), rounding=ROUND_DOWN)
