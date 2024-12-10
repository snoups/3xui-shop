import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config

logger = logging.getLogger(__name__)


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for injecting a Config instance into handler data.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize the ConfigMiddleware.

        Arguments:
            config (Config): The Config instance to be injected.
        """
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler.

        Arguments:
            handler (Callable): The next handler in the middleware chain.
            event (TelegramObject): The incoming Telegram event.
            data (dict): The context data passed to the handler.

        Returns:
            Any: The result of the next handler.
        """
        data["config"] = self.config
        return await handler(event, data)
