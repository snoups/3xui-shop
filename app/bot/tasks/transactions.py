import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.utils.constants import TransactionStatus
from app.db.models import Transaction, User
from app.bot.services.vpn import VPNService
from app.config import Config

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

async def cleanup_expired_vpn_users(
    session_factory: async_sessionmaker,
    vpn_service: VPNService,
    config: Config
) -> None:
    async with session_factory() as session:
        stmt = select(User).where(User.server_id.isnot(None))
        result = await session.execute(stmt)
        users = result.scalars().all()

        now = datetime.now(timezone.utc).timestamp()
        deleted_count = 0

        for user in users:
            expiry_time = await vpn_service.get_expiry_time(user)
            if expiry_time and expiry_time != 0:
                days_since_expiry = (now - expiry_time) / 86400  # 86400 секунд в сутках
                if days_since_expiry > config.shop.EXPIRED_SUBSCRIPTION_DELETION_PERIOD:
                    deleted = await vpn_service.delete_client(user)
                    if deleted:
                        user.server_id = None
                        await session.commit()
                        deleted_count += 1
                        logger.info(f"Deleted VPN client for user {user.tg_id} (expired {days_since_expiry:.1f} days ago)")
        try:
            await vpn_service.server_pool_service.sync_servers()
        except Exception as e:
            logger.error(f"Error during server sync: {e}")
            
        logger.info(f"[Cleanup] Deleted {deleted_count} expired VPN clients.")


def start_scheduler(session: async_sessionmaker, config: Config, vpn_service: VPNService = None) -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cancel_expired_transactions,
        "interval",
        minutes=15,
        args=[session],
        next_run_time=datetime.now(),
    )
    if vpn_service:
        scheduler.add_job(
            cleanup_expired_vpn_users,
            "interval",
            hours=6,
            args=[session, vpn_service, config.shop.EXPIRED_SUBSCRIPTION_DELETION_PERIOD],
            next_run_time=datetime.now(),
        )
    scheduler.start()
