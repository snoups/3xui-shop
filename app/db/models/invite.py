import logging
from datetime import datetime
from typing import Optional, Self

from sqlalchemy import Boolean, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.bot.utils.misc import generate_hash

from . import Base

logger = logging.getLogger(__name__)


class Invite(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hash_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    @classmethod
    async def create(cls, session: AsyncSession, name: str) -> Self:
        hash_code = generate_hash(name)
        invite = cls(name=name, hash_code=hash_code)
        session.add(invite)
        try:
            await session.commit()
            await session.refresh(invite)
            return invite
        except Exception as e:
            logger.error(f"Failed to create invite: {e}")
            await session.rollback()
            raise

    @classmethod
    async def get_by_hash(cls, session: AsyncSession, hash_code: str) -> Optional[Self]:
        result = await session.execute(select(cls).where(cls.hash_code == hash_code))
        return result.scalars().first()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[Self]:
        result = await session.execute(select(cls).order_by(cls.created_at.desc()))
        return list(result.scalars().all())

    @classmethod
    async def increment_clicks(cls, session: AsyncSession, invite_id: int) -> None:
        invite = await session.get(cls, invite_id)
        if invite:
            invite.clicks += 1
            await session.commit()
