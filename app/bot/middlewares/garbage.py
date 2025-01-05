from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import BotCommand, TelegramObject, Update

from app.bot.navigation import NavMain


class GarbageMiddleware(BaseMiddleware):
    """
    Middleware for deleting all incoming messages.

    This middleware deletes messages that are received from users.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Delete incoming message before passing the event to the handler.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler, which will be updated.

        Returns:
            Any: The result of calling the next handler with the updated data.
        """
        if isinstance(event, Update) and event.message:
            if event.message.from_user != event.bot.id and NavMain.START not in event.message.text:
                await event.message.delete()

        return await handler(event, data)
