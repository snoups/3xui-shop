from aiogram import Bot
from aiogram.types import LabeledPrice
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import SubscriptionCallback
from app.bot.services.plans import PlansService


class TelegramStars:
    """
    Service for handling payment creation using Telegram Stars.

    This service provides methods to create a payment link for a subscription based on traffic
    and duration. The payment is processed via Telegram's invoice system with specified prices.
    """

    async def create_payment(self, data: SubscriptionCallback, bot: Bot) -> str:
        """
        Create a payment link for the subscription.

        This method generates a payment link for a user subscription based on the provided data,
        including traffic and duration. It uses the Telegram bot's invoice creation system.

        Arguments:
            data (SubscriptionCallback): The data for the subscription, including traffic and duration.
            bot (Bot): The instance of the Bot for creating the invoice link.

        Returns:
            str: The generated payment link for the subscription.
        """
        prices = [LabeledPrice(label="XTR", amount=1)]
        # prices = [LabeledPrice(label="XTR", amount=data.price)]
        traffic = PlansService.convert_traffic_to_title(data.traffic)
        duration = PlansService.convert_days_to_period(data.duration)
        title = _("Subscription | traffic: {traffic}, duration: {duration}").format(
            traffic=traffic, duration=duration
        )
        description = _("traffic: {traffic}, duration: {duration}").format(
            traffic=traffic, duration=duration
        )
        return await bot.create_invoice_link(
            title=title,
            description=description,
            prices=prices,
            payload=data.pack(),
            currency="XTR",
        )
