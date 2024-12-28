import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class ServicesMiddleware(BaseMiddleware):
    """
    Middleware for injecting service instances into handler data.

    This middleware provides a way to inject various services, such as VPN and
    Plans services, into the handler's data. It helps centralize and
    share the service instances across all handlers.

    Attributes:
        services (dict[str, Any]): A dictionary containing various services to inject.
    """

    def __init__(self, **services) -> None:
        """
        Initializes the middleware with a list of services.

        Arguments:
            services (dict[str, Any]): A dictionary of service instances to be injected
                                       into handler data (e.g., VPN service, Plans service).
        """
        self.services = services
        logger.debug(f"ServicesMiddleware initialized with services: {list(services.keys())}")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler that injects services into the handler data.

        This method updates the handler data dictionary with the provided services,
        making them available to the handler for further processing.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Any: The result of calling the next handler with the updated data containing services.
        """
        data.update(self.services)
        return await handler(event, data)
