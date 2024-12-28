import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Update
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin

logger = logging.getLogger(__name__)


class MaintenanceMiddleware(BaseMiddleware):
    """
    Middleware to restrict non-admin and non-dev users during maintenance mode.
    """

    active: bool = False

    @classmethod
    def set_mode(cls, active: bool) -> None:
        """
        Enable or disable maintenance mode.

        Arguments:
            active (bool): True to enable, False to disable maintenance mode.
        """
        logger.info(f"Maintenance Mode: {'enabled' if active else 'disabled'}")
        cls.active = active

    def __init__(self, bot: Bot) -> None:
        """Initialize the middleware."""
        self.bot = bot
        logger.debug("MaintenanceMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Process incoming events and enforce maintenance mode restrictions.

        Arguments:
            handler (Callable): Next handler in the middleware chain.
            event (TelegramObject): Incoming Telegram event (e.g., message or callback).
            data (dict): Handler data passed to the middleware.

        Returns:
            Any: Handler result if maintenance mode allows processing, else None.
        """
        if isinstance(event, Update):

            if event.message:
                user_id = event.message.from_user.id
                is_admin = await IsAdmin()(event.message)
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
                is_admin = await IsAdmin()(event.callback_query)
            else:
                return await handler(event, data)

            if self.active and not (is_admin, user_id == self.bot.id):
                logger.info(f"User {user_id} tried to interact with the bot during maintenance.")
                if event.message:
                    await event.message.answer(_("The bot is in maintenance mode. Please wait."))
                elif event.callback_query:
                    await event.callback_query.answer(
                        _("The bot is in maintenance mode. Please wait."), show_alert=True
                    )
                return None
            else:
                return await handler(event, data)
