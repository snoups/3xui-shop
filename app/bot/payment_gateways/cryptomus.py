from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.payment_gateways import PaymentGateway


class Cryptomus(PaymentGateway):
    """
    Service for creating payments through the Cryptomus platform.
    """

    name = "Cryptomus"
    symbol = "$"
    code = "USD"
    callback = NavSubscription.PAY_CRYPTOMUS

    def create_payment(self, data: SubscriptionData) -> str:
        """
        Create a payment link for the subscription using Cryptomus.

        This method generates a payment link based on the provided subscription data.

        Arguments:
            data (SubscriptionData): The subscription data, including devices and duration.

        Returns:
            str: A URL for the payment link to complete the subscription process.
        """
        pass
