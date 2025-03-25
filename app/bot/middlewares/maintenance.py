import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from aiogram.types import User as TelegramUser
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.services import NotificationService

logger = logging.getLogger(__name__)


class MaintenanceMiddleware(BaseMiddleware):
    active: bool = False

    def __init__(self) -> None:
        logger.debug("Maintenance Middleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            user: TelegramUser | None = event.event.from_user

            if user is not None:
                is_admin = await IsAdmin()(user_id=user.id)
                logger.debug(f"Is user {user.id} an admin? {'Yes' if is_admin else 'No'}")

                if self.active and not is_admin and user.id != event.bot.id:
                    logger.info(f"User {user.id} tried to use bot in maintenance")
                    
                    if event.message:
                        message = event.message
                    elif event.callback_query and event.callback_query.message:
                        message = event.callback_query.message

                    if message:
                        await NotificationService.notify_by_message(
                            message=message,
                            text=_("maintenance:ntf:try_later"),
                            duration=5,
                        )

                    return None
                else:
                    logger.debug(f"User {user.id} is allowed to interact with the bot.")

        return await handler(event, data)

    @classmethod
    def set_mode(cls, active: bool) -> None:
        MaintenanceMiddleware.active = active
        logger.info(f"Maintenance Mode: {'enabled' if active else 'disabled'}")
