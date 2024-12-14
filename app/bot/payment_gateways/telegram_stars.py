import json

from aiogram import Bot
from aiogram.types import LabeledPrice


class TelegramStars:
    async def create_payment(self, data: dict, bot: Bot) -> str:
        prices = [LabeledPrice(label="XTR", amount=1)]
        return await bot.create_invoice_link(
            title=f"Subscription to VPN | Plan: {data["traffic"]}, Duration: {data["duration"]}",
            description=f"Plan: {data["traffic"]}, Duration: {data["duration"]}",
            prices=prices,
            payload=json.dumps(data),
            currency="XTR",
        )
