from sqlalchemy import *
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ._base import Base


class User(Base):
    """
    Model representing User table.

    Inherits from the Base class.
    """

    __tablename__ = "users"

    id = Column(
        Integer,  # not BigInteger
        primary_key=True,
        autoincrement=True,
    )
    state = Column(
        VARCHAR(length=6),
        nullable=False,
        default="guest",  # "guest" (not sub), "member" (sub), "admin"
    )
    user_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    first_name = Column(
        VARCHAR(length=128),
        nullable=False,
    )
    username = Column(
        VARCHAR(length=64),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    @staticmethod
    async def get(session: AsyncSession, **kwargs) -> "User":
        """
        Get a user from the database based on the specified filters.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for selecting the user.

        Returns:
            User: The user object or None if not found.
        """
        filters = [*[getattr(User, key) == v for key, v in kwargs.items()]]
        query = await session.execute(select(User).where(*filters))
        return query.scalar()

    @staticmethod
    async def get_or_create(session: AsyncSession, user_id: int, **kwargs) -> "User":
        """
        Get a user from the database based on the specified filters,
        or create a new user if not found.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The ID of the user.
            kwargs (dict): Additional parameters for creating a new user.

        Returns:
            User: The user object.
        """
        filters = [User.user_id == user_id]
        result = await session.execute(select(User).filter(*filters))

        try:
            user = result.scalar_one()
            for key, value in kwargs.items():
                setattr(user, key, value)
        except NoResultFound:
            user = User(user_id=user_id, **kwargs)
            session.add(user)

        await session.commit()
        return user

    @staticmethod
    async def update(session: AsyncSession, user_id: int, **kwargs) -> None:
        """
        Update a user in the database based on the specified filters.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The ID of the user to be updated.
            kwargs (dict): The attributes to be updated.
        """
        filters = [User.user_id == user_id]
        await session.execute(update(User).filter(*filters).values(**kwargs))
        await session.commit()

    @staticmethod
    async def is_exist(session: AsyncSession, **kwargs) -> bool:
        """
        Check if a user with the given ID exists in the database.

        Args:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict):  The filters for querying the existence of a User object.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        filters = [*[getattr(User, key) == v for key, v in kwargs.items()]]
        query = await session.execute(select(User).filter(*filters))
        return bool(query.scalar())
