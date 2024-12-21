from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ._base import Base


class Promocode(Base):
    """
    Model representing the Promocode table.
    """

    __tablename__ = "promocodes"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    code = Column(
        String(length=8),
        unique=True,
        nullable=False,
    )
    traffic = Column(
        BigInteger,
        nullable=False,
    )
    duration = Column(
        BigInteger,
        nullable=False,
    )
    is_activated = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    activated_by = Column(
        Integer,
        nullable=True,
    )

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> "Promocode | None":
        """
        Get a promocode from the database based on the specified filters.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for selecting the promocode.

        Returns:
            Optional[Promocode]: The promocode object or None if not found.
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
            Optional[Promocode]: The created promocode object, or None if creation failed.
        """
        promocode = Promocode(**kwargs)
        session.add(promocode)

        await session.commit()
        return promocode

    @classmethod
    async def update(cls, session: AsyncSession, code: str, **kwargs) -> None:
        """
        Update a promocode in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            code (str): The unique promocode string.
            kwargs (dict): Attributes to be updated.
        """
        filters = [Promocode.code == code]
        await session.execute(update(Promocode).filter(*filters).values(**kwargs))
        await session.commit()

    @classmethod
    async def exists(cls, session: AsyncSession, **kwargs) -> bool:
        """
        Check if a promocode exists in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            kwargs (dict): The filters for checking the promocode.

        Returns:
            bool: True if the promocode exists, otherwise False.
        """
        filters = [*[getattr(Promocode, key) == value for key, value in kwargs.items()]]
        query = await session.execute(select(Promocode).filter(*filters))
        return query.scalar() is not None
