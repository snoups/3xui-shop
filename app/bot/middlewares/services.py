import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class ServicesMiddleware(BaseMiddleware):
    """
    Middleware for injecting service instances into handler data.

    This middleware allows for injecting various service instances (such as VPNService)
    into handler data, making them accessible within handlers.
    """

    def __init__(self, **services) -> None:
        """
        Initializes the ServicesMiddleware with a list of services to inject.

        Arguments:
            services (dict[str, Any]): Any additional services to be injected.
        """
        self.services = services

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler to inject services into handler data.

        Arguments:
            handler (Callable): The handler function to process the event.
            event (TelegramObject): The incoming Telegram event.
            data (dict): Context data passed to the handler.

        Returns:
            Any: The result of the next handler with injected services.
        """
        data.update(self.services)
        return await handler(event, data)
