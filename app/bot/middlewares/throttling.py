from typing import Any, Awaitable, Callable, MutableMapping, Optional

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for handling throttling.
    """

    def __init__(
        self,
        *,
        default_key: Optional[str] = "default",
        default_ttl: float = 0.5,
        **ttl_map: float,
    ) -> None:
        """
        Initialize the ThrottlingMiddleware.

        Args:
            default_key (Optional[str]): The default key for throttling.
            default_ttl (float): The default time-to-live (TTL) in seconds for the default key.
            ttl_map (float): Mapping of keys to corresponding TTL values.
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
        Call the middleware.

        Args:
            handler (Callable): The handler function.
            event (TelegramObject): The Telegram event.
            data (dict): Additional data.
        """
        user: Optional[User] = data.get("event_from_user", None)

        if user is not None:
            throttling_key = get_flag(data, "throttling_key", default=self.default_key)
            if throttling_key and user.id in self.caches[throttling_key]:
                return None
            self.caches[throttling_key][user.id] = None

        return await handler(event, data)
