### origin
import logging
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey, Integer, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from . import Base

logger = logging.getLogger(__name__)


class Referral(Base):
    """
    Represents a referral where a user invites another user.

    Attributes:
        id (int): Unique primary key for the referral record.
        referrer_tg_id (int): Telegram user ID of the referrer.
        referred_tg_id (int): Unique Telegram user ID of the invited user (invitee).
        created_at (datetime): Timestamp when the referral record was created.
        referred_rewarded_at (datetime | None): Indicates whether the invited user has received their bonus.
        referrer_rewarded_at (datetime | None): Indicates whether the referrer has received their bonus.
        bonus_days (int): Number of subscription days granted as a reward for the referral.
        referred (User): Relationship to the user who has been invited.
        referrer (User): Relationship to the user who invited.
    """
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referred_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"), unique=True, nullable=False)  # deprecate
    referrer_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)  # deprecate
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    referred_rewarded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    referrer_rewarded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    bonus_days: Mapped[int] = mapped_column(Integer, nullable=False)
    referrer: Mapped["User"] = relationship(  # type: ignore
        "User",
        foreign_keys=[referrer_tg_id],  # type: ignore
        back_populates="sent_referrals"
    )
    referred: Mapped["User"] = relationship(  # type: ignore
        "User",
        foreign_keys=[referred_tg_id],  # type: ignore
        back_populates="referral"
    )

    def __repr__(self) -> str:
        return (
            f"<Referral(referrer_tg_id={self.referrer_tg_id}, "
            f"referred_tg_id={self.referred_tg_id}, "
            f"referred_rewarded_at={self.referred_rewarded_at}, "
            f"referrer_rewarded_at={self.referrer_rewarded_at}, "
            f"bonus_days={self.bonus_days})>"
        )

    @classmethod
    async def get_by_id(cls, session: AsyncSession, referral_id: int) -> Self | None:
        query = await session.execute(
            select(Referral).options(
                selectinload(Referral.referrer),
                selectinload(Referral.referred)
            ).where(Referral.id == referral_id)  # type: ignore
        )
        return query.scalar_one_or_none()

    @classmethod
    async def count_referrals(cls, session: AsyncSession, referrer_tg_id: int) -> int:
        query = await session.execute(
            select(func.count()).where(Referral.referrer_tg_id == referrer_tg_id)  # type: ignore
        )
        return query.scalar() or 0

    @classmethod
    async def get_referral(cls, session: AsyncSession, referred_tg_id: int) -> Self | None:
        query = await session.execute(
            select(Referral).options(selectinload(Referral.referrer)).where(
                Referral.referred_tg_id == referred_tg_id  # type: ignore
            )
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_referral_with_users(cls, session: AsyncSession, referred_tg_id: int) -> Self | None:
        query = await session.execute(
            select(Referral)
            .options(
                selectinload(Referral.referrer),
                selectinload(Referral.referred)
            )
            .where(Referral.referred_tg_id == referred_tg_id)  # type: ignore
        )
        return query.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, referrer_tg_id: int, referred_tg_id: int, bonus_days: int = 7) -> Self | None:
        existing_referral = await cls.get_referral(session, referred_tg_id)

        if existing_referral:
            logger.warning(f"User {referred_tg_id} is already invited by {existing_referral.referrer_tg_id}.")
            return False

        referral = Referral(
            referrer_tg_id=referrer_tg_id,
            referred_tg_id=referred_tg_id,
            bonus_days=bonus_days
        )
        session.add(referral)

        try:
            await session.commit()
            logger.info(f"Referral created: {referrer_tg_id} → {referred_tg_id}.")
            return referral
        except IntegrityError as exception:
            await session.rollback()
            logger.error(f"Error occurred while creating referral {referrer_tg_id} → {referred_tg_id}: {exception}")
            return False

    @classmethod
    async def set_rewarded(cls, session: AsyncSession, referral: Self) -> bool:
        """Sets up date and time of receiving rewards for the whole Referral: both referrer and referred users."""

        if referral.referred_rewarded_at and referral.referrer_rewarded_at:
            logger.info(f"Referral reward already given to {referral.referrer_tg_id} & {referral.referred_tg_id}.")
            return False

        await session.execute(
            update(Referral)
            .where(Referral.id == referral.id)  # type: ignore
            .values(
                referred_rewarded_at=func.now() if not referral.referred_rewarded_at else referral.referred_rewarded_at,
                referrer_rewarded_at=func.now() if not referral.referrer_rewarded_at else referral.referrer_rewarded_at
            )
        )
        await session.commit()

        logger.info(f"Referral reward granted for {referral.referrer_tg_id} & {referral.referred_tg_id}.")
        return True

    @classmethod
    async def rollback_rewarded(
            cls,
            session: AsyncSession,
            referral: Self,
            rollback_referrer: bool = True,
            rollback_referred: bool = True
    ) -> bool:
        await session.execute(
            update(Referral)
            .where(Referral.id == referral.id)  # type: ignore
            .values(
                referred_rewarded_at=None if rollback_referred else referral.referred_rewarded_at,
                referrer_rewarded_at=None if rollback_referrer else referral.referrer_rewarded_at
            )
        )
        await session.commit()

        logger.info(f"Referral reward rollback executed for {referral.referrer_tg_id} & {referral.referred_tg_id}.")
        return True

