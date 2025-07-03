import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import User, Server
from app.bot.services.vpn import VPNService
from app.config import Config

logger = logging.getLogger(__name__)


async def cleanup_expired_vpn_users(
    session_factory: async_sessionmaker,
    vpn_service: VPNService,
    config: Config,
) -> None:
    async with session_factory() as session:
        stmt = select(User).where(User.server_id.isnot(None))
        result = await session.execute(stmt)
        users = result.scalars().all()

        now = datetime.now(timezone.utc)
        deleted_count = 0
        users_to_update = []
        servers_to_refresh = set()

        for user in users:
            try:
                expiry_time = await vpn_service.get_expiry_time(user)
                if expiry_time and expiry_time != 0:
                    expiry_time = datetime.fromtimestamp(expiry_time / 1000, timezone.utc)
                    days_since_expiry = (now - expiry_time).days 
                    if days_since_expiry >= config.shop.EXPIRED_SUBSCRIPTION_DELETION_PERIOD:
                        deleted = await vpn_service.delete_client(user)
                        if deleted:
                            if user.server_id:
                                servers_to_refresh.add(user.server_id)
                            user.server_id = None
                            deleted_count += 1
                            users_to_update.append(user)
                            logger.info(
                                f"Deleted VPN client for user {user.tg_id} (expired {days_since_expiry:.1f} days ago)"
                            )
            except Exception as e:
                logger.error(f"Error processing user {getattr(user, 'tg_id', user)}: {e}")

        if users_to_update:
            await session.commit()

            for server_id in servers_to_refresh:
                server = await session.get(Server, server_id)
                if server:
                    await session.refresh(server, attribute_names=["users"])

        try:
            if users_to_update:
                await vpn_service.server_pool_service.sync_servers()
        except Exception as e:
            logger.error(f"Error during server sync: {e}")

        logger.info(f"[Cleanup] Deleted {deleted_count} expired VPN clients.")
        

def start_scheduler(session_factory: async_sessionmaker, vpn_service: VPNService, config: Config) -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cleanup_expired_vpn_users,
        "interval",
        hours=6,
        args=[session_factory, vpn_service, config],
        next_run_time=datetime.now(),
    )
    scheduler.start()