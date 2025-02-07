import logging

from aiogram import Bot

from app.bot.models import SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.utils.navigation import NavSubscription
from app.config import Config

logger = logging.getLogger(__name__)


class Cryptomus(PaymentGateway):
    name = "Cryptomus"
    symbol = "$"
    code = "USD"
    callback = NavSubscription.PAY_CRYPTOMUS

    def __init__(self, config: Config, bot: Bot):
        self.config = config
        self.bot = bot
        logger.info("Cryptomus payment gateway initialized.")

    def create_payment(self, data: SubscriptionData) -> str:
        pass
