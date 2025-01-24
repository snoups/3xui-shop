import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin

logger = logging.getLogger(__name__)


class MaintenanceMiddleware(BaseMiddleware):
    """
    Middleware to restrict access for non-admin users during maintenance mode.

    This middleware blocks non-admin users from interacting with the bot when maintenance
    mode is active. Admins and the bot itself are not restricted.

    Attributes:
        active (bool): Indicates whether maintenance mode is active. Defaults to False.
    """

    active: bool = False

    def __init__(self) -> None:
        """
        Initialize the middleware.
        """
        logger.debug("MaintenanceMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Restrict non-admin users during maintenance mode.

        This method checks whether maintenance mode is active and if the user is an admin.
        Non-admin users are blocked from interacting with the bot during maintenance mode.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Any: The result of the next handler if access is allowed, otherwise None.
        """
        if isinstance(event, Update):
            user: User | None = data.get("event_from_user", None)

            if user is not None:
                is_admin = await IsAdmin()(event.event)
                logger.debug(f"Is user {user.id} an admin? {'Yes' if is_admin else 'No'}")

                if self.active and not is_admin and user.id != event.bot.id:
                    logger.info(
                        f"User {user.id} tried to interact with the bot during maintenance."
                    )
                    text = _("🚧 The bot is in maintenance mode. Please wait.")

                    if event.message:
                        await event.message.answer(text=text, show_alert=True)
                    elif event.callback_query:
                        await event.callback_query.answer(text=text, show_alert=True)

                    return None
                else:
                    logger.debug(f"User {user.id} is allowed to interact with the bot.")

        return await handler(event, data)

    @classmethod
    def set_mode(cls, active: bool) -> None:
        """
        Enable or disable maintenance mode.

        Arguments:
            active (bool): True to enable maintenance mode, False to disable it.
        """
        logger.info(f"Maintenance Mode: {'enabled' if active else 'disabled'}")
        MaintenanceMiddleware.active = active
