from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .vpn import VPNService

import logging

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp.web import Application
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import SubscriptionData
from app.bot.payment_gateways import Cryptomus, PaymentGateway, TelegramStars, Yookassa
from app.bot.utils.constants import YOOKASSA_WEBHOOK
from app.bot.utils.navigation import NavSubscription
from app.config import Config

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(
        self,
        app: Application,
        config: Config,
        bot: Bot,
        session: async_sessionmaker,
        storage: RedisStorage,
        vpn_service: VPNService,
    ) -> None:
        self.gateways: dict[str, PaymentGateway] = {}
        self.session = session

        if config.yookassa.SHOP_ID and config.yookassa.TOKEN:
            yookassa = Yookassa(config, bot, session, storage, vpn_service)
            self.gateways[NavSubscription.PAY_YOOKASSA] = yookassa
            app.router.add_post(
                YOOKASSA_WEBHOOK,
                lambda request: yookassa.webhook_handler(request),
            )
        self.gateways[NavSubscription.PAY_TELEGRAM_STARS] = TelegramStars(config, bot)

        logger.info("Payment Service initialized.")

    def get_gateway(self, gateway_name: str) -> PaymentGateway | None:
        return self.gateways.get(gateway_name)

    async def create_payment(self, gateway: PaymentGateway, data: SubscriptionData) -> str:
        logger.debug(f"Creating payment with data: {data}")
        return await gateway.create_payment(self.session, data)
