import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from py3xui import AsyncApi

logger = logging.getLogger(__name__)


class ApiMiddleware(BaseMiddleware):
    """
    Middleware for injecting an AsyncApi instance into handler data.
    """

    def __init__(self, api: AsyncApi) -> None:
        """
        Initialize the ApiMiddleware.

        Arguments:
            api (AsyncApi): API instance to be injected.
        """
        self.api = api

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
        data["api"] = self.api
        return await handler(event, data)
