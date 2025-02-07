import logging

from aiogram import Bot
from aiogram.types import LabeledPrice
from aiogram.utils.i18n import gettext as _

from app.bot.models import SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.services.plan import PlanService
from app.bot.utils.navigation import NavSubscription
from app.config import Config

logger = logging.getLogger(__name__)


class TelegramStars(PaymentGateway):
    name = "TelegramStars"
    symbol = "★"
    code = "XTR"
    callback = NavSubscription.PAY_TELEGRAM_STARS

    def __init__(self, config: Config, bot: Bot):
        self.config = config
        self.bot = bot
        logger.info("TelegramStars payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        prices = [LabeledPrice(label="XTR", amount=1)]
        # prices = [LabeledPrice(label="XTR", amount=data.price)]
        devices = PlanService.convert_devices_to_title(data.devices)
        duration = PlanService.convert_days_to_period(data.duration)
        title = _("payment:invoice:title").format(devices=devices, duration=duration)
        description = _("payment:invoice:description").format(devices=devices, duration=duration)
        return await self.bot.create_invoice_link(
            title=title,
            description=description,
            prices=prices,
            payload=data.pack(),
            currency="XTR",
        )
