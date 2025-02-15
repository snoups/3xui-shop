from abc import ABC, abstractmethod

from app.bot.models import SubscriptionData
from app.bot.utils.constants import Currency, CurrencySymbol


class PaymentGateway(ABC):
    name: str
    currency: Currency
    symbol: CurrencySymbol
    callback: str

    @abstractmethod
    async def create_payment(self, data: SubscriptionData) -> str:
        pass

    @abstractmethod
    async def handle_payment_succeeded(self, payment_id: str) -> None:
        pass

    @abstractmethod
    async def handle_payment_canceled(self, payment_id: str) -> None:
        pass
