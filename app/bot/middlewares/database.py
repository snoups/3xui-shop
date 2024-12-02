from typing import Any, Awaitable, Callable, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import User


class DBSessionMiddleware(BaseMiddleware):
    """
    Middleware for handling database sessions.
    """

    def __init__(self, session: async_sessionmaker) -> None:
        """
        Initialize the DBSessionMiddleware.

        Args:
            session (async_sessionmaker): The async sessionmaker object for creating database sessions.
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
        Call the middleware.

        Args:
            handler (Callable): The handler function.
            event (TelegramObject): The Telegram event.
            data (dict): Additional data.
        """
        session: AsyncSession
        async with self.session() as session:
            user: Optional[TelegramUser] = data.get("event_from_user", None)

            if user is not None:
                user = await User.get_or_create(
                    session, user_id=user.id, first_name=user.first_name, username=user.username
                )
            data["user"] = user
            data["session"] = session
            return await handler(event, data)
