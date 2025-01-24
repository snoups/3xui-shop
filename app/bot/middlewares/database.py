import logging
import uuid
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import User

logger = logging.getLogger(__name__)


class DBSessionMiddleware(BaseMiddleware):
    """
    Middleware for managing database sessions and ensuring user existence in handlers.

    This middleware ensures that a database session is available for every handler.
    It also checks if the user exists in the database and creates a new user if necessary.

    Attributes:
        session (async_sessionmaker): A factory for creating async database sessions.
    """

    def __init__(self, session: async_sessionmaker) -> None:
        """
        Initializes middleware with a session factory for creating async database sessions.

        Arguments:
            session (async_sessionmaker): Session maker for async database sessions.
        """
        self.session = session
        logger.debug("DBSessionMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler that adds the database session and user to handler data.

        This method opens a new database session for every request. If the user is present
        in the event, it ensures that the user is stored in the database or retrieved if
        already exists. The session and user are then added to the handler's data dictionary.

        Arguments:
            handler (Callable): The handler function that processes the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Any: The result of calling the next handler with the updated data.
        """
        session: AsyncSession
        async with self.session() as session:
            user: TelegramUser | None = data.get("event_from_user", None)
            if user is not None and not user.is_bot:
                vpn_id = str(uuid.uuid4())
                logger.debug(f"Processing user {user.id} | {vpn_id}")
                user = await User.get_or_create(
                    session,
                    tg_id=user.id,
                    vpn_id=vpn_id,
                    first_name=user.first_name,
                    username=user.username,
                )
                logger.debug(f"User {user.id} created or fetched from the database.")
            else:
                logger.debug("No user found in event data.")

            data["user"] = user
            data["session"] = session
            logger.debug("Session and user added to handler data.")
            return await handler(event, data)
