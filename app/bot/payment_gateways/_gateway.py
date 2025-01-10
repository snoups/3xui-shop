from abc import ABC, abstractmethod

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.navigation import SubscriptionData


class PaymentGateway(ABC):
    """
    Abstract base class for payment gateways.

    Each gateway should implement its own version of the methods defined here.

    Attributes:
        name (str): Name of the payment gateway.
        symbol (str): The symbol used for the payment.
        code (str): The payment code.
        callback (str): The callback string for payment status.
    """

    name: str
    symbol: str
    code: str
    callback = str

    @abstractmethod
    async def create_payment(
        self,
        session: AsyncSession,
        data: SubscriptionData,
        bot: Bot = None,
    ) -> str:
        """
        Create a payment link or handle the payment process.

        Arguments:
            data (SubscriptionData): The subscription or payment data, including plan details.
            bot (Bot | None): Optional bot instance, required for gateways like TelegramStars.

        Returns:
            str: The payment link or confirmation, depending on the payment gateway.
        """
        pass
