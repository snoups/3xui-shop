import hashlib
import logging
from typing import Any, Awaitable, Callable, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import User

logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseMiddleware):
    """
    Middleware for managing database sessions in handlers.
    """

    def __init__(self, session: async_sessionmaker) -> None:
        """
        Initialize the database session middleware.

        Arguments:
            session (async_sessionmaker): Factory for creating asynchronous database sessions.
        """
        super().__init__()
        self.session = session

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Process the incoming Telegram event and inject a database session.

        Arguments:
            handler (Callable): The handler function to process the event.
            event (TelegramObject): The incoming Telegram event.
            data (dict): Contextual data passed to the handler.
        """
        session: AsyncSession
        async with self.session() as session:
            user: Optional[TelegramUser] = data.get("event_from_user", None)
            hash = hashlib.md5(str(user.id).encode()).hexdigest()
            if user is not None:
                user = await User.get_or_create(
                    session,
                    vpn_id=hash,
                    user_id=user.id,
                    first_name=user.first_name,
                    username=user.username,
                )
            data["user"] = user
            data["session"] = session
            return await handler(event, data)
