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
    Middleware for managing database sessions in handlers.

    This middleware ensures that a database session is available for every handler.
    It also manages user creation in the database if the user is not already present.

    Attributes:
        session (async_sessionmaker): A factory for creating async database sessions.
    """

    def __init__(self, session: async_sessionmaker) -> None:
        """
        Initializes the middleware with a session factory.

        Arguments:
            session (async_sessionmaker): A session maker that creates async database sessions.
        """
        super().__init__()
        self.session = session
        logger.info("DBSessionMiddleware initialized.")

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler that injects the database session and user into the handler data.

        This method opens a new database session for every request. If a user is present
        in the event, it will ensure that the user is stored in the database. Then, the
        session and user objects are added to the handler's data dictionary.

        Arguments:
            handler (Callable): The handler function to process the incoming event.
            event (TelegramObject): The incoming Telegram event (message, callback, etc.).
            data (dict): The data dictionary passed to the handler.

        Returns:
            Any: The result of calling the next handler with the injected database session and user.
        """
        session: AsyncSession
        async with self.session() as session:
            user: TelegramUser | None = data.get("event_from_user", None)
            if user is not None and not user.is_bot:
                vpn_id = str(uuid.uuid4())
                logger.debug(f"Processing user with ID: {user.id}, VPN ID: {vpn_id}")
                user = await User.get_or_create(
                    session,
                    vpn_id=vpn_id,
                    user_id=user.id,
                    first_name=user.first_name,
                    username=user.username,
                )
                logger.debug(f"User with ID: {user.id} created or fetched from the database.")
            else:
                logger.debug("No user found in event data.")

            data["user"] = user
            data["session"] = session
            logger.debug("Session and user added to handler data.")
            return await handler(event, data)
