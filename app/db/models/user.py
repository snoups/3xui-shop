from sqlalchemy import *
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ._base import Base


class User(Base):
    """
    Model representing the User table in the database.

    This model is used to store user information related to the bot, including their
    unique ID, VPN ID, and other personal details.
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
            kwargs (dict): The filters for selecting the user (e.g., user_id=123456).

        Returns:
            User | None: The user object if found, or None if not found.

        Example:
            user = await User.get(session, user_id=123456)
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
            user_id (int): The unique Telegram user ID.
            kwargs (dict): Additional attributes for the user if creating a new one (e.g., vpn_id).

        Returns:
            User: The user object.

        Example:
            user = await User.get_or_create(session, user_id=123456, vpn_id="vpn123")
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

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ValueError(
                f"Error during user {user_id} creation or update, possibly due to integrity issues."
            )

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
        filters = [User.user_id == user_id]
        await session.execute(update(User).filter(*filters).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, **kwargs) -> bool:
        """
        Check if a user exists in the database based on the provided filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for checking the user (e.g., user_id=123456).

        Returns:
            bool: True if the user exists, otherwise False.

        Example:
            exists = await User.exists(session, user_id=123456)
        """
        filters = [*[getattr(User, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(User).filter(*filters))
        return query.scalar() is not None
