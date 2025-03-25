import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.services import ReferralService
from app.db.models import ReferrerReward

logger = logging.getLogger(__name__)


async def reward_pending_referrals_after_payment(
    session_factory: async_sessionmaker,
    referral_service: ReferralService,
) -> None:
    session: AsyncSession
    async with session_factory() as session:
        stmt = select(ReferrerReward).where(ReferrerReward.rewarded_at.is_(None))
        result = await session.execute(stmt)
        pending_rewards = result.scalars().all()

        logger.info(f"[Background check] Found {len(pending_rewards)} not proceed rewards.")

        for reward in pending_rewards:
            success = await referral_service.process_referrer_rewards_after_payment(reward=reward)
            if not success:
                logger.warning(
                    f"[Background check] Reward {reward.id} was NOT proceed successfully."
                )

        logger.info("[Background check] Referrer rewards check finished.")


def start_scheduler(
    session_factory: async_sessionmaker,
    referral_service: ReferralService,
) -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        reward_pending_referrals_after_payment,
        "interval",
        minutes=15,
        args=[session_factory, referral_service],
        next_run_time=datetime.now(),
    )
    scheduler.start()
