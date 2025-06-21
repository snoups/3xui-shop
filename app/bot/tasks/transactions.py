import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.utils.constants import TransactionStatus
from app.db.models import Transaction

logger = logging.getLogger(__name__)


async def cancel_expired_transactions(
    session_factory: async_sessionmaker,
    expiration_minutes: int = 15,
) -> None:
    session: AsyncSession
    async with session_factory() as session:
        expiration_time = datetime.now(timezone.utc) - timedelta(minutes=expiration_minutes)
        stmt = select(Transaction).where(
            Transaction.status == TransactionStatus.PENDING,
            Transaction.created_at <= expiration_time,
        )
        result = await session.execute(stmt)
        expired_transactions = result.scalars().all()

        if expired_transactions:
            logger.info(
                f"[Background check] Found {len(expired_transactions)} expired transactions."
            )

            for transaction in expired_transactions:
                transaction.status = TransactionStatus.CANCELED
            await session.commit()

            logger.info("[Background check] Successfully canceled expired transactions.")
        else:
            logger.info("[Background check] No expired transactions found.")


def start_scheduler(session: async_sessionmaker) -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cancel_expired_transactions,
        "interval",
        minutes=15,
        args=[session],
        next_run_time=datetime.now(),
    )
    scheduler.start()
