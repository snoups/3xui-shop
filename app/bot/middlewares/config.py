from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for passing config data.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the ConfigMiddleware.

        Args:
            config (Config): The config data to be passed.
        """
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Call the middleware.

        Args:
            handler (Callable): The handler function.
            event (TelegramObject): The Telegram event.
            data (dict): Additional data.
        """
        data["config"] = self.config
        return await handler(event, data)
