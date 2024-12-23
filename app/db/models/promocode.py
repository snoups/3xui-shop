from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ._base import Base


class Promocode(Base):
    """
    Model representing the Promocode table in the database.

    This model is used to store and manage promocodes, which can be associated with
    subscription traffic and duration.
    """

    __tablename__ = "promocodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(length=8), unique=True, nullable=False)
    traffic = Column(BigInteger, nullable=False)
    duration = Column(BigInteger, nullable=False)
    is_activated = Column(Boolean, default=False, nullable=False)
    activated_by = Column(Integer, nullable=True)

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> "Promocode | None":
        """
        Get a promocode from the database based on the specified filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for selecting the promocode (e.g., code="ABC123").

        Returns:
            Promocode | None: The promocode object if found, or None if not found.

        Example:
            promocode = await Promocode.get(session, code="ABC123")
        """
        filters = [*[getattr(Promocode, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(Promocode).where(*filters))
        return query.scalar()

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Promocode | None":
        """
        Create a new promocode in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): Attributes for the new promocode.

        Returns:
            Promocode | None: The created promocode if successful, None if creation failed.

        Example:
            promocode = await Promocode.create(session, code="ABC123", traffic=1000, duration=3600)
        """
        promocode = Promocode(**kwargs)
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
            code (str): The unique promocode string (e.g., "ABC123").
            kwargs (dict): Attributes to be updated (e.g., traffic=2000, is_activated=True).

        Example:
            await Promocode.update(session, code="ABC123", traffic=2000, is_activated=True)
        """
        filters = [Promocode.code == code]
        await session.execute(update(Promocode).filter(*filters).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, **kwargs) -> bool:
        """
        Check if a promocode exists in the database based on the provided filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for checking the promocode (e.g., code="ABC123").

        Returns:
            bool: True if the promocode exists, otherwise False.

        Example:
            exists = await Promocode.exists(session, code="ABC123")
        """
        filters = [*[getattr(Promocode, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(Promocode).filter(*filters))
        return query.scalar() is not None
