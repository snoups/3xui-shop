import logging
from mailbox import Message
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.bot.utils.navigation import NavMain

logger = logging.getLogger(__name__)


class GarbageMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        logger.debug("Garbage Middleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update) and event.message:
            user_id = event.message.from_user.id

            if user_id == event.bot.id:
                logger.debug(f"Message from bot {event.bot.id} skipped.")
            elif (
                event.message.text
                and not event.message.text.endswith(NavMain.START)
                or event.message.forward_from
            ):
                try:
                    await event.message.delete()
                    logger.debug(f"Message {event.message.text} from user {user_id} deleted.")
                except Exception as exception:
                    logger.error(f"Failed to delete message from user {user_id}: {exception}")

        return await handler(event, data)
