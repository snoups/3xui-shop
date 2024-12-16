import logging
import math
import time
from datetime import datetime, timezone

from aiogram.utils.i18n import ngettext as _

UNLIMITED = "∞"


logger = logging.getLogger(__name__)


class ClientService:
    """
    Service for managing client data related to traffic and subscription expiry.

    This service processes and formats client data, including traffic usage,
    remaining quota, and subscription expiry time. It provides human-readable
    outputs for these values and checks for traffic or subscription expiration.

    Attributes:
        client_data (dict): Dictionary containing client-related data such as traffic and expiry.
    """

    def __init__(self, client_data: dict) -> None:
        """
        Initialize the ClientService instance.

        Arguments:
            client_data (dict): A dictionary containing client data.
        """
        self.client_data = client_data

    def __bool__(self) -> bool:
        """
        Return whether the client data exists.

        Returns:
            bool: True if client data exists, False otherwise.
        """
        return bool(self.client_data)

    @property
    def traffic_total(self) -> str:
        """
        Return the total subscription traffic in a human-readable format.

        Returns:
            str: Total traffic in a human-readable format.
        """
        return self._convert_size(self.client_data.get("traffic_total", 0))

    @property
    def traffic_remaining(self) -> str:
        """
        Return the remaining traffic in a human-readable format.

        Returns:
            str: Remaining traffic in a human-readable format.
        """
        return self._convert_size(self.client_data.get("traffic_remaining", 0))

    @property
    def traffic_used(self) -> str:
        """
        Return the used traffic in a human-readable format.

        Returns:
            str: Used traffic in a human-readable format.
        """
        return self._convert_size(self.client_data.get("traffic_used", 0))

    @property
    def traffic_up(self) -> str:
        """
        Return the uploaded traffic in a human-readable format.

        Returns:
            str: Uploaded traffic in a human-readable format.
        """
        return self._convert_size(self.client_data.get("traffic_up", 0))

    @property
    def traffic_down(self) -> str:
        """
        Return the downloaded traffic in a human-readable format.

        Returns:
            str: Downloaded traffic in a human-readable format.
        """
        return self._convert_size(self.client_data.get("traffic_down", 0))

    @property
    def expiry_time(self) -> str:
        """
        Return the time remaining until the subscription expires in a human-readable format.

        Returns:
            str: Time left until subscription expiry.
        """
        return self._time_left_to_expiry(self.client_data.get("expiry_time", 0))

    @property
    def has_traffic_expired(self) -> bool:
        """
        Check if the client's traffic has expired.

        Returns:
            bool: True if traffic expired, False otherwise.
        """
        remaining_traffic = self.client_data.get("remaining_traffic", -1)
        if remaining_traffic == -1:
            return False  # Unlimited traffic
        return remaining_traffic <= 0

    @property
    def has_subscription_expired(self) -> bool:
        """
        Check if the client's subscription has expired.

        Returns:
            bool: True if the subscription expired, False otherwise.
        """
        expiry_time = self.client_data.get("expiry_time", -1)
        if expiry_time == -1:
            return False  # Unlimited subscription

        current_time = time.time() * 1000
        return current_time > expiry_time

    def _convert_size(self, size_bytes: int) -> str:
        """
        Convert a size in bytes to a human-readable format.

        Arguments:
            size_bytes (int): Size in bytes.

        Returns:
            str: The size in a human-readable format.
        """
        if size_bytes == -1:
            return UNLIMITED
        elif size_bytes == 0:
            return f"{size_bytes} {_('B')}"

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
        i = min(int(math.floor(math.log(max(size_bytes, 1), 1024))), len(size_units_keys) - 1)
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        if s.is_integer():
            s = int(s)

        return f"{s} {size_units_keys[i]}"

    def _time_left_to_expiry(self, expiry_time: int) -> str:
        """
        Calculate the time left until subscription expiry.

        Arguments:
            expiry_time (int): The expiry timestamp in milliseconds.

        Returns:
            str: The remaining time in a human-readable format.
        """
        if expiry_time == -1:
            return UNLIMITED

        now = datetime.now(tz=timezone.utc)
        expiry_datetime = datetime.fromtimestamp(expiry_time / 1000, tz=timezone.utc)
        time_left = expiry_datetime - now

        days, remainder = divmod(time_left.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        return f"{int(days)}{_('d')}, {int(hours)}{_('h')}, {int(minutes)}{_('m')}"
