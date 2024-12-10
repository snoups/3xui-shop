from app.bot.payment_gateways import Cryptomus, TelegramStars, Yookassa


class PaymentService:
    def __init__(self) -> None:
        self.payment_gateways = {
            "yookassa": Yookassa(),
            "telegram_stars": TelegramStars(),
            "cryptomus": Cryptomus(),
        }

    def create_payment(self, gateway: str, amount: float, user_id: int) -> str:
        pass
