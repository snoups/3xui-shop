from app.bot.navigation import SubscriptionCallback


class Yookassa:
    """
    Service for creating payments through the Yookassa platform.

    This class handles the payment creation process using the Yookassa API, generating
    payment links or processing payment requests for subscriptions.
    """

    def create_payment(self, data: SubscriptionCallback) -> str:
        """
        Create a payment link for the subscription using Yookassa.

        This method generates a payment link based on the provided subscription data.

        Arguments:
            data (SubscriptionCallback): The subscription data, including devices and duration.

        Returns:
            str: The payment link for the subscription.
        """
        pass
