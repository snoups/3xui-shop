from typing import Any, Awaitable, Callable, MutableMapping, Optional

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for managing throttling of user requests.
    """

    def __init__(
        self,
        *,
        default_key: Optional[str] = "default",
        default_ttl: float = 0.5,
        **ttl_map: float,
    ) -> None:
        """
        Initializes the ThrottlingMiddleware.

        Args:
            default_key (Optional[str]): The default key used for throttling.
            default_ttl (float): The default time-to-live (TTL) in seconds for the default key.
            ttl_map (float): A mapping of throttling keys to their corresponding TTL values.
        """
        if default_key:
            ttl_map[default_key] = default_ttl

        self.default_key = default_key
        self.caches: dict[str, MutableMapping[int, None]] = {}

        for name, ttl in ttl_map.items():
            self.caches[name] = TTLCache(maxsize=10_000, ttl=ttl)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Optional[Any]:
        """
        Invokes the middleware for handling throttling logic.

        Args:
            handler (Callable): The handler function to process the event.
            event (TelegramObject): The Telegram event being processed.
            data (dict): Additional data passed to the handler.

        Returns:
            Optional[Any]: The result of the handler or None if the request is throttled.
        """
        user: Optional[User] = data.get("event_from_user", None)

        if user is not None:
            throttling_key = get_flag(data, "throttling_key", default=self.default_key)
            if throttling_key and user.id in self.caches[throttling_key]:
                return None
            self.caches[throttling_key][user.id] = None

        return await handler(event, data)
