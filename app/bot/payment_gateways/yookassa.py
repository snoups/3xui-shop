from aiogram.utils.i18n import gettext as _
from yookassa import Configuration, Payment
from yookassa.domain.models import Amount
from yookassa.domain.models.confirmation.request.confirmation_redirect import (
    ConfirmationRedirect,
)
from yookassa.domain.response import PaymentResponse

from app.bot.navigation import SubscriptionCallback


class Yookassa:
    """
    Service for creating payments through the Yookassa platform.

    This class handles the payment creation process using the Yookassa API, generating
    payment links or processing payment requests for subscriptions.
    """

    def __init__(self, shop_id: str, secret_key: str):
        """
        Initialize the Yookassa service with shop credentials.

        Arguments:
            shop_id (str): Your Yookassa Shop ID.
            secret_key (str): Your Yookassa Secret Key.
        """
        Configuration.configure(shop_id, secret_key)

    def create_payment(self, data: SubscriptionCallback) -> str:
        """
        Create a payment link for the subscription using Yookassa.

        This method generates a payment link based on the provided subscription data.

        Arguments:
            data (SubscriptionCallback): The subscription data, including devices and duration.

        Returns:
            str: The payment link for the subscription.
        """
        amount = Amount(value=str(data.price), currency="RUB")
        confirmation = ConfirmationRedirect(return_url="https://example.ru")
        description = _("Subscription | {devices} for {duration}").format(
            devices=data.devices, duration=data.duration
        )

        payment: PaymentResponse = Payment.create(
            amount=amount,
            description=description,
            confirmation=confirmation,
        )

        return payment.confirmation
