import logging
from datetime import datetime
from typing import Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.bot.utils.misc import generate_code

from . import Base

logger = logging.getLogger(__name__)


class Promocode(Base):
    """
    Represents a promocode entity in the database.

    Attributes:
        id (int): Unique identifier (primary key)
        code (str): Unique promocode value (8 characters max)
        duration (int): Associated subscription duration in days
        is_activated (bool): Flag indicating activation status
        activated_by (int | None): Telegram ID of activating user
        created_at (datetime): Timestamp of creation
        activated_user (User | None): Relationship to User model
    """

    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    is_activated: Mapped[bool] = mapped_column(default=False, nullable=False)
    activated_by: Mapped[int | None] = mapped_column(ForeignKey("users.tg_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    activated_user: Mapped["User | None"] = relationship(  # type: ignore
        "User", back_populates="activated_promocodes"
    )

    def __repr__(self) -> str:
        return (
            f"<Promocode(id={self.id}, code='{self.code}', duration={self.duration}, "
            f"is_activated={self.is_activated}, activated_by={self.activated_by}, "
            f"created_at={self.created_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, code: str) -> Self | None:
        filter = [Promocode.code == code]
        query = await session.execute(
            select(Promocode).options(selectinload(Promocode.activated_user)).where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs: Any) -> Self | None:
        while True:
            code = generate_code()
            promocode = await Promocode.get(session=session, code=code)
            if not promocode:
                break

        promocode = Promocode(code=code, **kwargs)
        session.add(promocode)

        try:
            await session.commit()
            logger.info(f"Promocode {promocode.code} created.")
            return promocode
        except IntegrityError as exception:
            await session.rollback()
            logger.error(f"Error occurred while creating promocode {promocode.code}: {exception}")
            return None

    @classmethod
    async def update(cls, session: AsyncSession, code: str, **kwargs: Any) -> Self | None:
        promocode = await Promocode.get(session=session, code=code)

        if not promocode:
            logger.warning(f"Promocode {code} not found for update.")
            return None

        # if promocode.is_activated:
        #     logger.warning(f"Promocode {code} is activated and cannot be updated.")
        #     return None

        filter = [Promocode.code == code]
        await session.execute(update(Promocode).where(*filter).values(**kwargs))
        await session.commit()
        logger.info(f"Promocode {code} updated.")
        return promocode

    @classmethod
    async def delete(cls, session: AsyncSession, code: str) -> bool:
        promocode = await Promocode.get(session=session, code=code)

        if promocode:
            await session.delete(promocode)
            await session.commit()
            logger.info(f"Promocode {code} deleted.")
            return True

        logger.warning(f"Promocode {code} not found for deletion.")
        return False

    @classmethod
    async def set_activated(cls, session: AsyncSession, code: str, user_id: int) -> bool:
        promocode = await Promocode.get(session=session, code=code)

        if not promocode:
            logger.warning(f"Promocode {code} not found for activation.")
            return False

        if promocode.is_activated:
            logger.warning(f"Promocode {code} is already activated.")
            return False

        await Promocode.update(session=session, code=code, is_activated=True, activated_by=user_id)
        return True

    @classmethod
    async def set_deactivated(cls, session: AsyncSession, code: str) -> bool:
        promocode = await Promocode.get(session=session, code=code)

        if not promocode:
            logger.warning(f"Promocode {code} not found for deactivation.")
            return False

        if not promocode.is_activated:
            logger.warning(f"Promocode {code} is already deactivated.")
            return False

        await Promocode.update(session=session, code=code, is_activated=False, activated_by=None)
        return True
