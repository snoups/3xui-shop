import logging

from aiogram import Bot
from aiogram.utils.i18n import lazy_gettext as __

from app.bot.models import SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.utils.constants import Currency
from app.bot.utils.navigation import NavSubscription
from app.config import Config

logger = logging.getLogger(__name__)


class Cryptomus(PaymentGateway):
    name = ""
    currency = Currency.USD
    callback = NavSubscription.PAY_CRYPTOMUS

    def __init__(self, config: Config, bot: Bot) -> None:
        self.name = __("payment:gateway:cryptomus")
        self.config = config
        self.bot = bot
        logger.info("Cryptomus payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        pass

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        logger.info(f"Payment succeeded {payment_id}")
        pass

    async def handle_payment_canceled(self, payment_id: str) -> None:
        logger.info(f"Payment canceled {payment_id}")
        pass
