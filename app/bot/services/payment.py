from enum import Enum

from app.bot.payment_gateways import Cryptomus, TelegramStars, Yookassa


class PaymentMethod(Enum):
    PAY_YOOKASSA = ("pay_yookassa", "₽", "RUB")
    PAY_TELEGRAM_STARS = ("pay_telegram_stars", "★", "XTR")
    PAY_CRYPTOMUS = ("pay_cryptomus", "$", "USD")

    def __init__(self, callback_data, symbol, code):
        self.callback_data = callback_data
        self.symbol = symbol
        self.code = code

    @classmethod
    def get_by_callback_data(cls, callback_data):
        for method in cls:
            if method.callback_data == callback_data:
                return method
        return None


class PaymentService:
    def __init__(self) -> None:
        self.payment_gateways = {
            "yookassa": Yookassa(),
            "telegram_stars": TelegramStars(),
            "cryptomus": Cryptomus(),
        }

    def create_payment(self, gateway: str, amount: float, user_id: int) -> str:
        pass
