from datetime import datetime
from typing import Optional

from sqlalchemy import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class User(Base):
    """
    Model representing the User table.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(length=6), nullable=False, default="guest")
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=128), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> Optional["User"]:
        """
        Get a user from the database based on the specified filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for selecting the user.

        Returns:
            Optional[User]: The user object or None if not found.
        """
        filters = [getattr(cls, key) == value for key, value in kwargs.items()]
        query = await session.execute(select(cls).filter(*filters))
        return query.scalar()

    @classmethod
    async def get_or_create(cls, session: AsyncSession, user_id: int, **kwargs) -> "User":
        """
        Get a user from the database or create a new one if not found.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The Telegram user ID.
            kwargs (dict): Additional attributes for a new user.

        Returns:
            User: The user object.
        """
        filters = [cls.user_id == user_id]
        query = await session.execute(select(cls).filter(*filters))
        user = query.scalar()

        if user is None:
            user = cls(user_id=user_id, **kwargs)
            session.add(user)

        else:
            for key, value in kwargs.items():
                setattr(user, key, value)

        return user

    @classmethod
    async def update(cls, session: AsyncSession, user_id: int, **kwargs) -> None:
        """
        Update a user in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The ID of the user to be updated.
            kwargs (dict): Attributes to be updated.
        """
        await session.execute(update(cls).where(cls.user_id == user_id).values(**kwargs))

    @classmethod
    async def exists(cls, session: AsyncSession, **kwargs) -> bool:
        """
        Check if a user exists in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for checking the user.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        filters = [getattr(cls, key) == value for key, value in kwargs.items()]
        query = await session.execute(select(cls).filter(*filters).limit(1))
        return query.scalar() is not None
