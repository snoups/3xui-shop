import logging

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import lazy_gettext as __
from aiohttp.web import Application, Request, Response
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.utils.constants import CRYPTOMUS_WEBHOOK, Currency
from app.bot.utils.navigation import NavSubscription
from app.config import Config

logger = logging.getLogger(__name__)


class Cryptomus(PaymentGateway):
    name = ""
    currency = Currency.USD
    callback = NavSubscription.PAY_CRYPTOMUS

    def __init__(
        self,
        app: Application,
        config: Config,
        session: async_sessionmaker,
        storage: RedisStorage,
        bot: Bot,
        i18n: I18n,
        services: ServicesContainer,
    ):
        self.name = __("payment:gateway:cryptomus")
        self.app = app
        self.config = config
        self.session = session
        self.storage = storage
        self.bot = bot
        self.i18n = i18n
        self.services = services

        self.app.router.add_post(CRYPTOMUS_WEBHOOK, lambda request: self.webhook_handler(request))
        logger.info("Cryptomus payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        pass

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        await self._on_payment_succeeded(payment_id)

    async def handle_payment_canceled(self, payment_id: str) -> None:
        await self._on_payment_canceled(payment_id)

    async def webhook_handler(self, request: Request) -> Response:
        pass
