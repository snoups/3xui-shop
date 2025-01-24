import logging
from datetime import datetime
from typing import Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from . import Base

logger = logging.getLogger(__name__)


class Promocode(Base):
    """
    Represents a Promocode in the database.

    Attributes:
        id (int): The unique promocode ID (primary key).
        code (str): The unique promocode code (maximum 8 characters).
        duration (int): The duration of the subscription associated with the promocode.
        is_activated (bool): Indicates whether the promocode has been activated.
        activated_by (int | None): The ID of the user who activated the promocode, if any.
        created_at (datetime): The timestamp when the promocode was created.
    """

    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(length=8), unique=True, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    is_activated: Mapped[bool] = mapped_column(default=False, nullable=False)
    activated_by: Mapped[int | None] = mapped_column(ForeignKey("users.tg_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    activated_user: Mapped["User"] = relationship("User", back_populates="activated_promocodes")  # type: ignore

    def __repr__(self) -> str:
        """
        Represents the Promocode object as a string.

        Returns:
            str: A string representation of the Promocode object.
        """
        return (
            f"<Promocode(id={self.id}, code='{self.code}', duration={self.duration}, "
            f"is_activated={self.is_activated}, activated_by={self.activated_by}, "
            f"created_at={self.created_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, code: str) -> Self | None:
        """
        Retrieve a promocode by its code.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The unique promocode code.

        Returns:
            Promocode | None: The promocode object if found, otherwise None.

        Example:
            promocode = await Promocode.get(session, code='ABC123')
        """
        filter = [Promocode.code == code]
        query = await session.execute(
            select(Promocode).options(selectinload(Promocode.activated_user)).where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, code: str, **kwargs) -> Self | None:
        """
        Create a new promocode.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The unique promocode code.
            kwargs (dict): Additional attributes for the new promocode (e.g., duration).

        Returns:
            Promocode | None: The created promocode if successful, None if creation failed.

        Example:
            promocode = await Promocode.create(session, code="ABC123", duration=3600)
        """
        promocode = await Promocode.get(session, code)

        if promocode is None:
            promocode = Promocode(code=code, **kwargs)
            session.add(promocode)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return None

        return promocode

    @classmethod
    async def update(cls, session: AsyncSession, code: str, **kwargs) -> None:
        """
        Update attributes of a promocode.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to update.
            kwargs (dict): Attributes to update (e.g., duration=30, is_activated=True).

        Example:
            await Promocode.update(session, code="ABC123", is_activated=True)
        """
        filter = [Promocode.code == code]
        await session.execute(update(Promocode).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def delete(cls, session: AsyncSession, code: str) -> bool:
        """
        Delete a promocode by its code.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to delete.

        Returns:
            bool: True if the promocode was deleted, False otherwise.

        Example:
            deleted = await Promocode.delete(session, code="ABC123")
        """
        filter = [Promocode.code == code]
        query = await session.execute(select(Promocode).where(*filter))
        promocode = query.scalar_one_or_none()

        if promocode:
            await session.delete(promocode)
            await session.commit()
            return True
        else:
            return False

    @classmethod
    async def exists(cls, session: AsyncSession, code: str) -> bool:
        """
        Check if a promocode exists.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to check.

        Returns:
            bool: True if the promocode exists, otherwise False.

        Example:
            exists = await Promocode.exists(session, code="ABC123")
        """
        return await Promocode.get(session, code) is not None
