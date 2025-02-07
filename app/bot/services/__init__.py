from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp.web import Application
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer
from app.config import Config

from .notification import NotificationService
from .payment import PaymentService
from .plan import PlanService
from .server_pool import ServerPoolService
from .vpn import VPNService


async def initialize(
    app: Application,
    config: Config,
    bot: Bot,
    session: async_sessionmaker,
    storage: RedisStorage,
) -> ServicesContainer:
    server_pool = ServerPoolService(config, session)
    plan = PlanService()
    vpn = VPNService(session, server_pool)
    payment = PaymentService(app, config, bot, session, storage, vpn)
    notification = NotificationService(config, bot)

    return ServicesContainer(
        server_pool=server_pool,
        plan=plan,
        vpn=vpn,
        payment=payment,
        notification=notification,
    )
