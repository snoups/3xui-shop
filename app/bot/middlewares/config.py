import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config

logger = logging.getLogger(__name__)


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for injecting a Config instance into handler data.

    This middleware ensures that a configuration object (`Config`) is accessible
    in every handler's data dictionary, allowing all handlers to use the same
    configuration values without having to pass them explicitly.

    Attributes:
        config (Config): The `Config` instance to be injected into handler data.
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes the middleware with the given `Config` instance.

        Arguments:
            config (Config): The `Config` instance that will be injected into
                             handler data, making it globally available to all handlers.
        """
        self.config = config
        logger.info("ConfigMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler that adds the `Config` instance to the handler data.

        This method is called for every update, and it adds the `Config` instance
        to the handler's data dictionary. After that, it calls the next handler in the
        middleware chain.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler, which will be updated.

        Returns:
            Any: The result of calling the next handler with the updated data.
        """
        data["config"] = self.config
        return await handler(event, data)
