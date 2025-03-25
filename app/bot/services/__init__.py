from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer
from app.config import Config

from .notification import NotificationService
from .plan import PlanService
from .referral import ReferralService
from .server_pool import ServerPoolService
from .subscription import SubscriptionService
from .vpn import VPNService


async def initialize(
    config: Config,
    session: async_sessionmaker,
    bot: Bot,
) -> ServicesContainer:
    server_pool = ServerPoolService(config=config, session=session)
    plan = PlanService()
    vpn = VPNService(config=config, session=session, server_pool_service=server_pool)
    notification = NotificationService(config=config, bot=bot)
    referral = ReferralService(config=config, session_factory=session, vpn_service=vpn)
    subscription = SubscriptionService(config=config, session_factory=session, vpn_service=vpn)

    return ServicesContainer(
        server_pool=server_pool,
        plan=plan,
        vpn=vpn,
        notification=notification,
        referral=referral,
        subscription=subscription,
    )
