from abc import ABC, abstractmethod

from app.bot.models import SubscriptionData


class PaymentGateway(ABC):
    name: str
    symbol: str
    code: str
    callback = str

    @abstractmethod
    async def create_payment(self, data: SubscriptionData) -> str:
        pass
