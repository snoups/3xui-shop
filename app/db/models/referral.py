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
        referrer_tg_id (int): Unique Telegram user ID of the referrer.
        referred_tg_id (int): Unique Telegram user ID of the invited user (invitee).
        created_at (datetime): Timestamp when the referral record was created.
        referred_rewarded_at (datetime | None): Indicates whether the invited user has received its 'Try for free' bonus.
        referred_bonus_days (int | None): Number of subscription days granted as a reward to a referred user by 'Try for free'.
        referred (User): Relationship to the user who has been invited.
        referrer (User): Relationship to the user who invited.
    """

    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    referred_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    referrer_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    referred_rewarded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    referred_bonus_days: Mapped[int] = mapped_column(Integer, nullable=True)
    referrer: Mapped["User"] = relationship(  # type: ignore
        "User", foreign_keys=[referrer_tg_id], back_populates="referrals_sent"  # type: ignore
    )
    referred: Mapped["User"] = relationship(  # type: ignore
        "User", foreign_keys=[referred_tg_id], back_populates="referral"  # type: ignore
    )

    def __repr__(self) -> str:
        return (
            f"<Referral(id={self.id}, "
            f"referred_tg_id={self.referred_tg_id}, "
            f"referrer_tg_id={self.referrer_tg_id}, "
            f"referred_rewarded_at={self.referred_rewarded_at}, "
            f"referred_bonus_days={self.referred_bonus_days})>"
        )

    @classmethod
    async def get_by_id(cls, session: AsyncSession, referral_id: int) -> Self | None:
        filters = [Referral.id == referral_id]

        query = await session.execute(
            select(Referral)
            .options(selectinload(Referral.referrer), selectinload(Referral.referred))
            .where(*filters)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_referral_count(cls, session: AsyncSession, referrer_tg_id: int) -> int:
        filters = [Referral.referrer_tg_id == referrer_tg_id]

        query = await session.execute(select(func.count()).where(*filters))
        return query.scalar() or 0

    @classmethod
    async def get_referral(cls, session: AsyncSession, referred_tg_id: int) -> Self | None:
        filters = [Referral.referred_tg_id == referred_tg_id]

        query = await session.execute(
            select(Referral).options(selectinload(Referral.referrer)).where(*filters)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_referral_with_users(
        cls, session: AsyncSession, referred_tg_id: int
    ) -> Self | None:
        filters = [Referral.referred_tg_id == referred_tg_id]

        query = await session.execute(
            select(Referral)
            .options(selectinload(Referral.referrer), selectinload(Referral.referred))
            .where(*filters)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        referrer_tg_id: int,
        referred_tg_id: int,
    ) -> Self | None:
        """
        Creates new referral relation between invited (referred) user and a user who invited him (referred).

        Args:
            session (AsyncSession): Active database session.
            referred_tg_id(int): Unique telegram id of the referred user.
            referrer_tg_id(int): Unique telegram id of the referrer user.

        Returns:
            bool: True if rewards successfully marked, False if duplicate rewards detected.
        """
        existing_referral = await cls.get_referral(session, referred_tg_id)

        if existing_referral:
            logger.warning(
                f"User {referred_tg_id} is already invited by {existing_referral.referrer_tg_id}."
            )
            return False

        referral = Referral(
            referrer_tg_id=referrer_tg_id,
            referred_tg_id=referred_tg_id,
        )
        session.add(referral)

        try:
            await session.commit()
            logger.info(f"Referral created: {referrer_tg_id} → {referred_tg_id}.")
            return referral
        except IntegrityError as exception:
            await session.rollback()
            logger.error(
                f"Error occurred while creating referral {referrer_tg_id} → {referred_tg_id}: {exception}"
            )
            return False

    @classmethod
    async def set_rewarded(
        cls,
        session: AsyncSession,
        referral: Self,
        referred_bonus_days: int,
    ) -> bool:
        """
        Marks referral and/or referrer as rewarded and assigns bonus days.

        Args:
            session (AsyncSession): Active database session.
            referral (Self): Referral instance to update.
            referred_bonus_days (int): Bonus days granted to the referred.

        Returns:
            bool: True if reward successfully marked, False otherwise.
        """
        filters = [Referral.id == referral.id]

        await session.execute(
            update(Referral)
            .where(*filters)  # type: ignore
            .values(
                referred_rewarded_at=func.now(),
                referred_bonus_days=referred_bonus_days,
            )
        )
        await session.commit()
        await session.refresh(referral)

        logger.info(f"Referred {referral.referred_tg_id} received {referred_bonus_days} bonus days")
        return True

    @classmethod
    async def rollback_rewarded(
        cls,
        session: AsyncSession,
        referral: Self,
    ) -> bool:
        """
        This method allows to cancel the referred reward.

        Args:
            session (AsyncSession): The active database session.
            referral (Self): The referral object to rollback rewards for.

        Returns:
            bool: True if rollback was successful, False otherwise.
        """
        filters = [Referral.id == referral.id]

        await session.execute(
            update(Referral)
            .where(*filters)  # type: ignore
            .values(
                referred_rewarded_at=None,
                referred_bonus_days=None,
            )
        )
        await session.commit()
        await session.refresh(referral)

        logger.info(f"Referral reward rollback successful for {referral.referred_tg_id}.")
        return True
