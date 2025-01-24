import logging
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey, String, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from . import Base

logger = logging.getLogger(__name__)


class User(Base):
    """
    Represents the User table in the database.

    Attributes:
        id (int): The unique primary key for the user.
        tg_id (int): The unique Telegram user ID.
        vpn_id (str): The unique VPN identifier for the user.
        server_id (int | None): The foreign key referencing the server.
        first_name (str): The first name of the user.
        username (str | None): The Telegram username of the user.
        created_at (datetime): The timestamp when the user was created.
        server (Server | None): The associated server object (if any).
        transactions (list[Transaction]): The list of transactions associated with the user.
        activated_promocodes (list[Promocode]): The promocodes activated by the user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    vpn_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    server_id: Mapped[int | None] = mapped_column(
        ForeignKey("servers.id", ondelete="SET NULL"), nullable=True
    )

    first_name: Mapped[str] = mapped_column(String(length=32), nullable=False)
    username: Mapped[str | None] = mapped_column(String(length=32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    server: Mapped["Server | None"] = relationship("Server", back_populates="users", uselist=False)  # type: ignore
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")  # type: ignore
    activated_promocodes: Mapped[list["Promocode"]] = relationship(  # type: ignore
        "Promocode", back_populates="activated_user"
    )

    def __repr__(self) -> str:
        """
        Represents the User object as a string.

        Returns:
            str: A string representation of the User object.
        """
        return (
            f"<User(id={self.id}, tg_id={self.tg_id}, vpn_id='{self.vpn_id}', "
            f"server_id={self.server_id}, first_name='{self.first_name}', "
            f"username='{self.username}', created_at={self.created_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, tg_id: int) -> Self | None:
        """
        Retrieve a user by Telegram ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            tg_id (int): The unique Telegram user ID.

        Returns:
            User | None: The user object if found, otherwise None.

        Example:
            user = await User.get(session, tg_id=123456)
        """
        filter = [User.tg_id == tg_id]
        query = await session.execute(
            select(User)
            .options(
                selectinload(User.transactions),
                selectinload(User.activated_promocodes),
                selectinload(User.server),
            )
            .where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_or_create(cls, session: AsyncSession, tg_id: int, **kwargs) -> Self | None:
        """
        Retrieve a user or create one if not found.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            tg_id (int): The unique Telegram user ID.
            kwargs (dict): Additional attributes for creating a new user.

        Returns:
            User | None: The user object if found or successfully created, otherwise None.

        Example:
            user = await User.get_or_create(session, tg_id=123456, vpn_id="vpn123")
        """
        user = await User.get(session, tg_id)

        if user is None:
            user = User(tg_id=tg_id, **kwargs)
            session.add(user)
            try:
                await session.commit()
            except IntegrityError as exception:
                await session.rollback()
                logger.error(f"Error occurred while creating user {tg_id}: {exception}")
                return None

        return user

    @classmethod
    async def update(cls, session: AsyncSession, tg_id: int, **kwargs) -> None:
        """
        Update a user's attributes.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            tg_id (int): The unique Telegram user ID.
            kwargs (dict): Attributes to be updated (e.g., first_name="John").

        Example:
            await User.update(session, tg_id=123456, first_name="John")
        """
        filter = [User.tg_id == tg_id]
        await session.execute(update(User).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, tg_id: int) -> bool:
        """
        Check if a user exists by Telegram ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            tg_id (int): The unique Telegram user ID.

        Returns:
            bool: True if the user exists, otherwise False.

        Example:
            exists = await User.exists(session, tg_id=123456)
        """
        return await User.get(session, tg_id) is not None
