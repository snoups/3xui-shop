import logging
import math
import time
from datetime import datetime, timezone

from aiogram.utils.i18n import gettext as _

from app.bot.utils.constants import UNLIMITED

logger = logging.getLogger(__name__)


class ClientData:
    def __init__(
        self,
        max_devices: int,
        traffic_total: int,
        traffic_remaining: int,
        traffic_used: int,
        traffic_up: int,
        traffic_down: int,
        expiry_time: str,
    ) -> None:
        self._max_devices = max_devices
        self._traffic_total = traffic_total
        self._traffic_remaining = traffic_remaining
        self._traffic_used = traffic_used
        self._traffic_up = traffic_up
        self._traffic_down = traffic_down
        self._expiry_time = expiry_time
        logger.debug(f"ClientData initialized: {self.__str__()}")

    def __str__(self) -> str:
        return (
            f"ClientData(max_devices={self._max_devices}, traffic_total={self._traffic_total}, "
            f"traffic_remaining={self._traffic_remaining}, traffic_used={self._traffic_used}, "
            f"traffic_up={self._traffic_up}, traffic_down={self._traffic_down}, "
            f"expiry_time={self._expiry_time})"
        )

    @property
    def max_devices(self) -> str:
        devices = self._max_devices
        if devices == -1:
            return UNLIMITED
        return devices

    @property
    def traffic_total(self) -> str:
        return self._convert_size(self._traffic_total)

    @property
    def traffic_remaining(self) -> str:
        return self._convert_size(self._traffic_remaining)

    @property
    def traffic_used(self) -> str:
        return self._convert_size(self._traffic_used)

    @property
    def traffic_up(self) -> str:
        return self._convert_size(self._traffic_up)

    @property
    def traffic_down(self) -> str:
        return self._convert_size(self._traffic_down)

    @property
    def expiry_time(self) -> str:
        return self._time_left_to_expiry(self._expiry_time)

    @property
    def has_subscription_expired(self) -> bool:
        current_time = time.time() * 1000
        expired = self._expiry_time != -1 and current_time > self._expiry_time
        logger.debug(f"Subscription expired: {expired}")
        return expired

    def _convert_size(self, size_bytes: int) -> str:
        try:
            if size_bytes == -1:
                return UNLIMITED
            elif size_bytes == 0:
                return f"{size_bytes} {_('MB')}"

            size_units_keys = [_("MB"), _("GB"), _("TB"), _("PB"), _("EB"), _("ZB"), _("YB")]
            size_in_mb = max(size_bytes / 1024**2, 1)
            i = min(int(math.floor(math.log(size_in_mb, 1024))), len(size_units_keys) - 1)
            p = math.pow(1024, i)
            s = round(size_in_mb / p, 2)

            if s.is_integer():
                s = int(s)

            result = f"{s} {size_units_keys[i]}"
            logger.debug(f"Converted size: {size_bytes} bytes to {result}")
            return result
        except Exception as exception:
            logger.error(f"Error converting size: {exception}")
            return f"0 {_('MB')}"

    def _time_left_to_expiry(self, expiry_time: int) -> str:
        try:
            if expiry_time == -1:
                return UNLIMITED

            now = datetime.now(tz=timezone.utc)
            expiry_datetime = datetime.fromtimestamp(expiry_time / 1000, tz=timezone.utc)
            time_left = expiry_datetime - now

            days, remainder = divmod(time_left.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes = remainder // 60

            result_parts = []
            if days > 0:
                result_parts.append(f"{int(days)}{_('d')}")
            if hours > 0:
                result_parts.append(f"{int(hours)}{_('h')}")
            if minutes > 0 or not result_parts:
                result_parts.append(f"{int(minutes)}{_('m')}")

            result = " ".join(result_parts)
            logger.debug(f"Time left to expiry: {result}")
            return result
        except Exception as exception:
            logger.error(f"Error calculating time to expiry: {exception}")
            return f"0{_('m')}"
