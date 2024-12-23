import logging
from typing import Any, Awaitable, Callable, MutableMapping

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, User
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for controlling the rate of requests from users.

    This middleware prevents spamming and ensures that users cannot make requests
    too quickly by implementing a time-to-live (TTL) cache for user actions. It
    manages rate limiting by checking whether a user has exceeded the allowed
    request frequency.

    Attributes:
        default_key (str | None): The default key used for throttling.
        default_ttl (float): The default TTL (time-to-live) for user actions, in seconds.
        caches (dict[str, MutableMapping[int, None]]): A dictionary of TTL caches for
                                                       each throttling key.
    """

    def __init__(
        self,
        *,
        default_key: str | None = "default",
        default_ttl: float = 0.5,
        **ttl_map: float,
    ) -> None:
        """
        Initializes the middleware with specified throttling settings.

        Arguments:
            default_key (Optional[str]): The default key used for throttling.
            default_ttl (float): The default time-to-live (TTL) for the default key.
            ttl_map (float): A dictionary of specific TTL values for each throttling key.
        """
        if default_key:
            ttl_map[default_key] = default_ttl

        self.default_key = default_key
        self.caches: dict[str, MutableMapping[int, None]] = {}

        for name, ttl in ttl_map.items():
            self.caches[name] = TTLCache(maxsize=10_000, ttl=ttl)
        logger.info("ThrottlingMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler that manages the throttling logic.

        This method checks if a user has exceeded the request frequency limit. If
        throttling is applied, it returns None to prevent the handler from being called.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Optional[Any]: The result of the handler, or None if the request is throttled.
        """
        if hasattr(event, "pre_checkout_query"):
            if getattr(event, "pre_checkout_query"):
                logger.debug("Pre-checkout query event, skipping throttling.")
                return await handler(event, data)

        if hasattr(event, "message"):
            if hasattr(event, "successful_payment"):
                if getattr(event, "successful_payment"):
                    logger.debug("Successful payment event, skipping throttling.")
                    return await handler(event, data)

        user: User | None = data.get("event_from_user", None)

        if user is not None:
            key = get_flag(data, "throttling_key", default=self.default_key)
            if key:
                if user.id in self.caches[key]:
                    logger.warning(f"User {user.id} is being throttled with key: {key}")
                    return None
                logger.debug(
                    f"User {user.id} is allowed to proceed, adding to cache with key: {key}",
                )
                self.caches[key][user.id] = None
            else:
                logger.debug(
                    f"No throttling key provided for user {user.id}, proceeding without throttle."
                )

        return await handler(event, data)
