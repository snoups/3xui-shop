from sqlalchemy import *
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ._base import Base


class User(Base):
    """
    Model representing the User table.
    """

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    vpn_id = Column(
        String(length=32),
        unique=True,
        nullable=False,
    )
    user_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
    )
    first_name = Column(
        String(length=128),
        nullable=False,
    )
    username = Column(
        String(length=64),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> "User | None":
        """
        Get a user from the database based on the specified filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for selecting the user.

        Returns:
            Optional[User]: The user object or None if not found.
        """
        filters = [*[getattr(User, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(User).where(*filters))
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
        filters = [User.user_id == user_id]
        result = await session.execute(select(User).filter(*filters))

        try:
            user = result.scalar_one()
            for key, value in kwargs.items():
                if key != "vpn_id":
                    setattr(user, key, value)
        except NoResultFound:
            user = User(user_id=user_id, **kwargs)
            session.add(user)

        await session.commit()
        return user

    @classmethod
    async def update(session: AsyncSession, user_id: int, **kwargs) -> None:
        """
        Update a user in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The ID of the user to be updated.
            kwargs (dict): Attributes to be updated.
        """
        filters = [User.user_id == user_id]
        await session.execute(update(User).filter(*filters).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(session: AsyncSession, **kwargs) -> bool:
        """
        Check if a user exists in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for checking the user.

        Returns:
            bool: True if the user exists, otherwise False.
        """
        filters = [*[getattr(User, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(User).filter(*filters))
        return query.scalar()
