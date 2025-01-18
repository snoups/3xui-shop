import logging
from datetime import datetime
from typing import Self

from sqlalchemy import String, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

logger = logging.getLogger(__name__)


class User(Base):
    """
    Model representing the User table in the database.

    Attributes:
        id (int): The unique user ID (primary key).
        vpn_id (str): The unique VPN identifier for the user.
        user_id (int): The unique Telegram user ID.
        first_name (str): The user's first name.
        username (str | None): The user's Telegram username.
        language_code (str | None): The user's language code (e.g., "en").
        created_at (datetime): The timestamp when the user was created.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vpn_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    username: Mapped[str | None] = mapped_column(String(length=32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, vpn_id='{self.vpn_id}', user_id={self.user_id}, "
            f"first_name={self.first_name}, username={self.username}, "
            f"created_at={self.created_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, user_id: int) -> Self | None:
        """
        Get a user by user_id.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique Telegram user ID.

        Returns:
            User | None: The user object if found, else None.

        Example:
            user = await User.get(session, user_id=123456)
        """
        filter = [User.user_id == user_id]
        query = await session.execute(select(User).where(*filter))
        return query.scalar_one_or_none()

    @classmethod
    async def get_or_create(cls, session: AsyncSession, user_id: int, **kwargs) -> Self | None:
        """
        Get a user or create a new one if not found.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique Telegram user ID.
            kwargs (dict): Additional attributes if creating a new user.

        Returns:
            User | None: The user object if found or created, else None.

        Example:
            user = await User.get_or_create(session, user_id=123456, vpn_id="vpn123")
        """
        filter = [User.user_id == user_id]
        query = await session.execute(select(User).where(*filter))
        user = query.scalar_one_or_none()

        if user is None:
            user = User(user_id=user_id, **kwargs)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as exception:
                await session.rollback()
                logger.error(f"Error occurred while creating user {user_id}: {exception}")
                return None

        return user

    @classmethod
    async def update(cls, session: AsyncSession, user_id: int, **kwargs) -> None:
        """
        Update a user in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique user ID.
            kwargs (dict): Attributes to be updated (e.g., first_name="John").

        Example:
            await User.update(session, user_id=123456, first_name="John")
        """
        filter = [User.user_id == user_id]
        await session.execute(update(User).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, user_id: int) -> bool:
        """
        Check if a user exists by user_id.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique Telegram user ID.

        Returns:
            bool: True if user exists, otherwise False.

        Example:
            exists = await User.exists(session, user_id=123456)
        """
        filter = [User.user_id == user_id]
        query = await session.execute(select(User).where(*filter))
        return query.scalar_one_or_none() is not None
