from aiogram import Bot
from aiogram.types import LabeledPrice
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.services.plan import PlanService


class TelegramStars(PaymentGateway):
    """
    Service for handling payment creation using Telegram Stars.
    """

    name = "TelegramStars"
    symbol = "★"
    code = "XTR"
    callback = NavSubscription.PAY_TELEGRAM_STARS

    async def create_payment(self, session, data: SubscriptionData, bot: Bot) -> str:
        """
        Create a payment link for the subscription.

        This method generates a payment link for a user subscription based on the provided data,
        including devices and duration. It uses the Telegram bot's invoice creation system.

        Arguments:
            data (SubscriptionData): The subscription data, including devices and duration.
            bot (Bot): The instance of the Bot for creating the invoice link.

        Returns:
            str: The generated payment link for the subscription.
        """
        prices = [LabeledPrice(label="XTR", amount=1)]
        # prices = [LabeledPrice(label="XTR", amount=data.price)]
        devices = PlanService.convert_devices_to_title(data.devices)
        duration = PlanService.convert_days_to_period(data.duration)
        title = _("Subscription | {devices} for {duration}").format(
            devices=devices, duration=duration
        )
        description = _("Subscription | {devices} for {duration}").format(
            devices=devices, duration=duration
        )
        return await bot.create_invoice_link(
            title=title,
            description=description,
            prices=prices,
            payload=data.pack(),
            currency="XTR",
        )
