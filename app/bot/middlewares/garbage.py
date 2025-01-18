import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.bot.navigation import NavMain

logger = logging.getLogger(__name__)


class GarbageMiddleware(BaseMiddleware):
    """
    Middleware for deleting all incoming messages.

    This middleware deletes messages that are received from users.
    """

    def __init__(self) -> None:
        """
        Initialize the middleware.
        """
        logger.debug("GarbageMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Delete incoming messages from users before passing the event to the handler.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Any: The result of calling the next handler with the updated data.
        """
        if isinstance(event, Update) and event.message:
            user_id = event.message.from_user.id

            if user_id == event.bot.id:
                logger.debug(f"Message from bot {event.bot.id} skipped.")
            elif event.message.text and NavMain.START not in event.message.text:
                try:
                    await event.message.delete()
                    logger.debug(f"Message from user {user_id} deleted.")
                except Exception as exception:
                    logger.error(f"Failed to delete message from user {user_id}: {exception}")
            else:
                logger.debug(f"Message from user {user_id} contains start command, not deleted.")
        else:
            logger.debug("Event is not a message, skipping.")

        return await handler(event, data)
