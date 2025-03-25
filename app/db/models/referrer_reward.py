import logging
from datetime import datetime
from decimal import Decimal
from typing import Self

from sqlalchemy import (
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.bot.utils.constants import ReferrerRewardLevel, ReferrerRewardType
from app.db.models import Base

logger = logging.getLogger(__name__)


class ReferrerReward(Base):
    """
    Represents a history of assigned and given rewards to a referrer users (ones who invited new user).

    Attributes:
        id (int): Unique primary key for the referral record.
        user_tg_id (int): Unique Telegram user ID of the user who is receiving a reward.
        reward_type (ReferrerRewardType): Type of reward, weather bonus days or money for user balance.
        reward_level (ReferrerRewardLevel): If rewarding referrer, here specify level of rewarding.
        amount (decimal): Amount of reward.
        created_at (datetime): Timestamp when the reward was created.
        rewarded_at (datetime | None): Indicates whether the specified user is rewarded.
        payment_id (str): Unique with user_tg_id payment_id of the transaction, just to avoid duplicates.
    """

    __tablename__ = "referrer_rewards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(
        ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False
    )
    reward_type: Mapped[ReferrerRewardType] = mapped_column(
        Enum(ReferrerRewardType), nullable=False
    )
    reward_level: Mapped[ReferrerRewardLevel] = mapped_column(
        Enum(ReferrerRewardLevel), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=38, scale=18), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    rewarded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    payment_id: Mapped[str] = mapped_column(String(length=64), nullable=False)

    __table_args__ = (UniqueConstraint("user_tg_id", "payment_id", name="uq_user_payment"),)

    def __repr__(self) -> str:
        return (
            f"<ReferrerReward(created_at={self.created_at}, "
            f"user_tg_id={self.user_tg_id}, "
            f"reward_type={self.reward_type.name}, "
            f"reward_level={self.reward_level.name}, "
            f"created_at={self.created_at},"
            f"rewarded_at={self.rewarded_at})>"
        )

    @validates("amount")
    def validate_amount(self, key, value):
        if hasattr(self, "reward_type"):
            if self.reward_type == ReferrerRewardType.DAYS and value != int(value):
                raise ValueError("Amount must be an integer when reward_type is DAYS.")
        return value

    @classmethod
    async def get_by_id(cls, session: AsyncSession, reward_id: int) -> Self | None:
        filters = [ReferrerReward.id == reward_id]

        query = await session.execute(select(ReferrerReward).where(*filters))

        return query.scalar_one_or_none()

    @classmethod
    async def get_rewards_sum(
        cls,
        session: AsyncSession,
        tg_id: int,
        reward_type: ReferrerRewardType,
        reward_level: ReferrerRewardLevel,
    ) -> Decimal:
        filters = [
            ReferrerReward.user_tg_id == tg_id,
            ReferrerReward.reward_type == reward_type,
            ReferrerReward.reward_level == reward_level,
        ]

        query = await session.execute(
            select(func.coalesce(func.sum(ReferrerReward.amount), 0)).where(*filters)
        )

        return query.scalar() or Decimal(0)

    @classmethod
    async def create_referrer_reward(
        cls,
        session: AsyncSession,
        user_tg_id: int,
        reward_type: ReferrerRewardType,
        amount: Decimal,
        payment_id: str,
        reward_level: ReferrerRewardLevel | None = None,
    ) -> Self | None:
        reward = ReferrerReward(
            user_tg_id=user_tg_id,
            reward_type=reward_type,
            reward_level=reward_level,
            amount=amount,
            payment_id=payment_id,
        )

        session.add(reward)
        try:
            await session.commit()
            logger.info(
                f"Referral reward created for user {user_tg_id}, type {reward_type}, amount {amount}"
            )
            return reward
        except IntegrityError as exception:
            await session.rollback()
            logger.error(f"Failed to create referral reward for user {user_tg_id}: {exception}")
            return None

    @classmethod
    async def get_pending_rewards(
        cls,
        session: AsyncSession,
        user_tg_id: int | None = None,
    ) -> list[Self]:
        filters = [ReferrerReward.rewarded_at.is_(None)]

        if user_tg_id is not None:
            filters.append(ReferrerReward.user_tg_id == user_tg_id)

        query = await session.execute(select(ReferrerReward).where(*filters))

        return query.scalars().all()

    @classmethod
    async def get_pending_rewards_count(
        cls,
        session: AsyncSession,
        user_tg_id: int | None = None,
    ) -> int:
        filters = [ReferrerReward.rewarded_at.is_(None)]

        if user_tg_id is not None:
            filters.append(ReferrerReward.user_tg_id == user_tg_id)

        query = await session.execute(
            select(func.count()).select_from(ReferrerReward).where(*filters)
        )

        return query.scalar_one()

    @classmethod
    async def mark_reward_as_given(cls, session: AsyncSession, reward: Self) -> Self | None:
        filters = [ReferrerReward.id == reward.id]

        try:
            await session.execute(
                update(ReferrerReward).where(*filters).values(rewarded_at=func.now())
            )
            await session.commit()
            logger.info(f"Marked reward {reward.id} as given.")
            return reward
        except Exception as exception:
            await session.rollback()
            logger.error(f"Failed to mark reward {reward.id} as given: {exception}")
            return False
