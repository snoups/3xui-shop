import logging
from typing import Any, Awaitable, Callable, MutableMapping

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject, Update
from aiogram.types import User as TelegramUser
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(
        self,
        *,
        default_key: str | None = "default",
        default_ttl: float = 0.3,
        **ttl_map: dict[str, float],
    ) -> None:
        if default_key:
            ttl_map[default_key] = default_ttl

        self.default_key = default_key
        self.caches: dict[str, MutableMapping[int, None]] = {}

        for name, ttl in ttl_map.items():
            self.caches[name] = TTLCache(maxsize=10_000, ttl=ttl)

        logger.debug("Throttling Middleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            logger.debug(f"Received event of type {type(event)}, skipping throttling.")
            return await handler(event, data)

        if event.pre_checkout_query:
            logger.debug("Pre-checkout query event, skipping throttling.")
            return await handler(event, data)

        if event.message and event.message.successful_payment:
            logger.debug("Successful payment event, skipping throttling.")
            return await handler(event, data)

        user: TelegramUser | None = event.event.from_user

        if user is not None:
            key = get_flag(handler=data, name="throttling_key", default=self.default_key)

            if key:
                if user.id in self.caches[key]:
                    logger.warning(f"User {user.id} throttled.")
                    return None
                logger.debug(f"User {user.id} not throttled.")
                self.caches[key][user.id] = None
            else:
                logger.debug(f"No throttle key for user {user.id}")

        return await handler(event, data)
