import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.utils.constants import TransactionStatus
from app.db.models import Transaction

logger = logging.getLogger(__name__)


async def cancel_expired_transactions(session: async_sessionmaker, expiration_minutes: int = 15):
    session: AsyncSession
    async with session() as session:
        expiration_time = datetime.now(timezone.utc) - timedelta(minutes=expiration_minutes)
        stmt = select(Transaction).where(
            Transaction.status == TransactionStatus.PENDING,
            Transaction.created_at <= expiration_time,
        )
        result = await session.execute(stmt)
        expired_transactions = result.scalars().all()

        for transaction in expired_transactions:
            transaction.status = TransactionStatus.CANCELED
        await session.commit()


def start_scheduler(session: async_sessionmaker):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cancel_expired_transactions,
        "interval",
        minutes=15,
        args=[session],
        next_run_time=datetime.now(),
    )
    scheduler.start()
