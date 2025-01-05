from datetime import datetime

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ._base import Base


class Promocode(Base):
    """
    Model representing the Promocode table in the database.

    This model is used to store and manage promocodes, which can be associated with
    subscription traffic and duration. Promocodes can also track whether they have
    been activated and by whom.
    """

    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(length=8), unique=True, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    is_activated: Mapped[bool] = mapped_column(default=False, nullable=False)
    activated_by: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    @classmethod
    async def get(cls, session: AsyncSession, code: str) -> "Promocode | None":
        """
        Get a promocode from the database based on the provided code.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to search for.

        Returns:
            Promocode | None: The promocode object if found, or None if not found.

        Example:
            promocode = await Promocode.get(session, code="ABC123")
        """
        filter = [Promocode.code == code]
        query = await session.execute(select(Promocode).where(*filter))
        return query.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, code: str, **kwargs) -> "Promocode | None":
        """
        Create a new promocode in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The unique promocode code.
            kwargs (dict): Additional attributes for the new promocode (e.g., duration).

        Returns:
            Promocode | None: The created promocode if successful, None if creation failed.

        Example:
            promocode = await Promocode.create(session, code="ABC123", duration=3600)
        """
        filter = [Promocode.code == code]
        query = await session.execute(select(Promocode).where(*filter))
        promocode = query.scalar_one_or_none()

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
        Update a promocode in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The unique promocode code (e.g., "ABC123").
            kwargs (dict): Attributes to be updated (e.g., duration=30, is_activated=True).

        Example:
            await Promocode.update(session, code="ABC123", duration=30, is_activated=True)
        """
        filter = [Promocode.code == code]
        await session.execute(update(Promocode).where(*filter).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, code: str) -> bool:
        """
        Check if a promocode with the given code exists in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to check for existence.

        Returns:
            bool: True if the promocode exists, otherwise False.

        Example:
            exists = await Promocode.exists(session, code="ABC123")
        """
        filter = [Promocode.code == code]
        query = await session.execute(select(Promocode).where(*filter))
        return query.scalar_one_or_none() is not None

    @classmethod
    async def delete(cls, session: AsyncSession, code: str) -> bool:
        """
        Delete a promocode from the database based on the promocode's code.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The promocode code to delete.

        Returns:
            bool: True if the promocode was successfully deleted, False otherwise.

        Example:
            deleted = await Promocode.delete(session, code="ABC123")
        """
        filter = [Promocode.code == code]
        async with session.begin():
            query = await session.execute(select(Promocode).where(*filter))
            promocode = query.scalar_one_or_none()

            if promocode:
                await session.delete(promocode)
                await session.commit()
                return True
            else:
                return False
