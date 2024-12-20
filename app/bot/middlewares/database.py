import hashlib
import logging
import uuid
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

    This middleware ensures that a database session is available for every handler,
    allowing access to the database and handling user creation if necessary.
    """

    def __init__(self, session: async_sessionmaker) -> None:
        """
        Initializes the DBSessionMiddleware with an async session factory.

        Arguments:
            session (async_sessionmaker): A factory for creating asynchronous database sessions.
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
        Middleware handler to inject the database session into handler data.

        Arguments:
            handler (Callable): The handler function to process the event.
            event (TelegramObject): The incoming Telegram event.
            data (dict): Context data passed to the handler.

        Returns:
            Any: The result of the handler with an injected database session and user.
        """
        session: AsyncSession
        async with self.session() as session:
            user: Optional[TelegramUser] = data.get("event_from_user", None)
            if user is not None:
                vpn_id = str(uuid.uuid4())
                user = await User.get_or_create(
                    session,
                    vpn_id=vpn_id,
                    user_id=user.id,
                    first_name=user.first_name,
                    username=user.username,
                )
            data["user"] = user
            data["session"] = session
            return await handler(event, data)
