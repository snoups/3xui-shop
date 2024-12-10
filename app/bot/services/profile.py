import logging
import math
import time
from datetime import datetime

from aiogram.utils.i18n import ngettext as _
from py3xui import Client

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Service for managing client profile data, including subscription and traffic checks.
    """

    def __init__(self, client: Client) -> None:
        """
        Initialize the ProfileService with client data.

        Arguments:
            client (Client): The client object retrieved from the XUI API.
        """
        self.client_data = self.parse_client_data(client)

    def parse_client_data(self, client: Client) -> dict:
        """
        Parse and structure client data from the XUI API.

        Arguments:
            client (Client): The client object containing subscription and traffic details.

        Returns:
            dict: Structured data with keys:
                  - "plan": Total traffic plan in bytes.
                  - "remaining_traffic": Remaining traffic in bytes.
                  - "expiry_time": Expiry timestamp in milliseconds.
                  - "total": Total traffic used in bytes.
                  - "up": Uploaded traffic in bytes.
                  - "down": Downloaded traffic in bytes.
        """
        try:
            if client is None:
                return {}

            if client.total == 0:
                remaining_traffic = -1
                plan = -1
            else:
                remaining_traffic = client.total - (client.up + client.down)
                plan = client.total

            total = client.up + client.down
            up = client.up
            down = client.down
            expiry_time = -1 if client.expiry_time == 0 else client.expiry_time

            return {
                "plan": plan,
                "remaining_traffic": remaining_traffic,
                "expiry_time": expiry_time,
                "total": total,
                "up": up,
                "down": down,
            }
        except Exception as exception:
            logger.error(f"Error processing client data: {exception}")
            return {}

    @property
    def plan(self) -> str:
        """Return the subscription plan in a human-readable format."""
        return self._convert_size(self.client_data["plan"])

    @property
    def remaining_traffic(self) -> str:
        """Return the remaining traffic in a human-readable format."""
        return self._convert_size(self.client_data["remaining_traffic"])

    @property
    def expiry_time(self) -> str:
        """Return the time left to expiry as a human-readable string."""
        return self._time_left_to_expiry()

    @property
    def total(self) -> str:
        """Return the total traffic in a human-readable format."""
        return self._convert_size(self.client_data["total"])

    @property
    def up(self) -> str:
        """Return the uploaded traffic in a human-readable format."""
        return self._convert_size(self.client_data["up"])

    @property
    def down(self) -> str:
        """Return the downloaded traffic in a human-readable format."""
        return self._convert_size(self.client_data["down"])

    def has_valid_data(self) -> bool:
        """
        Check if the client has valid data.

        Returns:
            bool: True if the client has valid data, False otherwise.
        """
        return bool(self.client_data)

    def has_subscription_expired(self) -> bool:
        """
        Check if the subscription has expired.

        Returns:
            bool: True if the subscription has expired, False otherwise.
                  Unlimited subscriptions (-1) always return False.
        """
        expiry_time = self.client_data.get("expiry_time", -1)
        if expiry_time == -1:
            return False  # Unlimited subscription

        current_time = time.time() * 1000
        return current_time > expiry_time

    def has_traffic_expired(self) -> bool:
        """
        Check if the traffic has expired (remaining traffic is 0 or less).

        Returns:
            bool: True if traffic has expired, False otherwise.
                  Unlimited traffic (-1) always returns False.
        """
        remaining_traffic = self.client_data.get("remaining_traffic", -1)
        if remaining_traffic == -1:
            return False  # Unlimited traffic
        return remaining_traffic <= 0

    def _convert_size(self, size_bytes: int) -> str:
        """
        Convert a file size from bytes to a human-readable format.

        Arguments:
            size_bytes (int): The size in bytes.

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

        return f"{s} {size_units_keys[i]}"

    def _time_left_to_expiry(self) -> str:
        """
        Calculate the time remaining until the subscription expires.

        Returns:
            str: A formatted string with the time left (e.g., '2d, 3h, 15m'),
                 or '∞' if the subscription is unlimited (-1).
        """
        expiry_time = self.client_data.get("expiry_time", -1)
        if expiry_time == -1:
            return "∞"

        now = datetime.now()
        expiry_datetime = datetime.fromtimestamp(expiry_time / 1000)

        time_left = expiry_datetime - now

        days, remainder = divmod(time_left.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        return f"{int(days)}{_('d')}, {int(hours)}{_('h')}, {int(minutes)}{_('m')}"
