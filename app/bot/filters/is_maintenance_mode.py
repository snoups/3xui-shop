import logging

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class IsMaintenanceMode(BaseFilter):
    """
    Filter to check if the bot is in maintenance mode.

    This filter blocks events when the bot is in maintenance mode.

    Attributes:
        active (bool): Indicates whether the bot is in maintenance mode.
                       True means maintenance mode is active, False means it's off.
    """

    active: bool = False

    @classmethod
    def set_mode(cls, active: bool) -> None:
        """
        Set the maintenance mode status.

        Arguments:
            active (bool): True to enable maintenance mode, False to disable.
        """
        logger.info(f"Maintenance Mode: {active}")
        cls.active = active

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Check if the bot is in maintenance mode.

        Arguments:
            event (TelegramObject): The event object (e.g., Message or CallbackQuery).

        Returns:
            bool: False if the bot is in maintenance mode, True otherwise.
        """
        return self.active
