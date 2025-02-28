import base64
import hashlib
import json
import logging
import uuid
from hmac import compare_digest

import aiohttp
from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiohttp.web import Application, Request, Response
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.utils.constants import CRYPTOMUS_WEBHOOK, Currency, TransactionStatus
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import Transaction

logger = logging.getLogger(__name__)


class Cryptomus(PaymentGateway):
    name = ""
    currency = Currency.USD
    callback = NavSubscription.PAY_CRYPTOMUS

    def __init__(
        self,
        app: Application,
        config: Config,
        session: async_sessionmaker,
        storage: RedisStorage,
        bot: Bot,
        i18n: I18n,
        services: ServicesContainer,
    ) -> None:
        self.name = __("payment:gateway:cryptomus")
        self.app = app
        self.config = config
        self.session = session
        self.storage = storage
        self.bot = bot
        self.i18n = i18n
        self.services = services

        self.app.router.add_post(CRYPTOMUS_WEBHOOK, self.webhook_handler)
        logger.info("Cryptomus payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        bot_username = (await self.bot.get_me()).username
        redirect_url = f"https://t.me/{bot_username}"
        order_id = str(uuid.uuid4())
        price = str(data.price)

        payload = {
            "amount": price,
            "currency": self.currency.code,
            "order_id": order_id,
            "url_return": redirect_url,
            "url_success": redirect_url,
            "url_callback": self.config.bot.DOMAIN + CRYPTOMUS_WEBHOOK,
            "lifetime": 1800,
            "is_payment_multiple": False,
        }
        headers = {
            "merchant": self.config.cryptomus.MERCHANT_ID,
            "sign": self.generate_signature(json.dumps(payload)),
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            url = "https://api.cryptomus.com/v1/payment"
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                if response.status == 200 and result.get("result", {}).get("url"):
                    pay_url = result["result"]["url"]
                else:
                    raise Exception(f"Error: {response.status}; Result: {result}; Data: {data}")

        async with self.session() as session:
            await Transaction.create(
                session=session,
                tg_id=data.user_id,
                subscription=data.pack(),
                payment_id=result["result"]["order_id"],
                status=TransactionStatus.PENDING,
            )

        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        return pay_url

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        await self._on_payment_succeeded(payment_id)

    async def handle_payment_canceled(self, payment_id: str) -> None:
        await self._on_payment_canceled(payment_id)

    async def webhook_handler(self, request: Request) -> Response:
        logger.debug(f"Received Cryptomus webhook request")
        try:
            event_json = await request.json()

            if not self.verify_webhook(request, event_json):
                return Response(status=403)

            match event_json.get("status"):
                case "paid" | "paid_over":
                    order_id = event_json.get("order_id")
                    await self.handle_payment_succeeded(order_id)
                    return Response(status=200)

                case "cancel":
                    order_id = event_json.get("order_id")
                    await self.handle_payment_canceled(order_id)
                    return Response(status=200)

                case _:
                    return Response(status=400)

        except Exception as exception:
            logger.exception(f"Error processing Cryptomus webhook: {exception}")
            return Response(status=400)

    def verify_webhook(self, request: Request, data: dict) -> bool:
        client_ip = (
            request.headers.get("CF-Connecting-IP")
            or request.headers.get("X-Real-IP")
            or request.headers.get("X-Forwarded-For")
            or request.remote
        )
        if client_ip not in ["91.227.144.54"]:
            logger.warning(f"Unauthorized IP: {client_ip}")
            return False

        sign = data.pop("sign", None)
        if not sign:
            logger.warning("Missing signature.")
            return False

        json_data = json.dumps(data, separators=(",", ":"))
        hash_value = self.generate_signature(json_data)

        if not compare_digest(hash_value, sign):
            logger.warning(f"Invalid signature.")
            return False

        return True

    def generate_signature(self, data: str) -> str:
        base64_encoded = base64.b64encode(data.encode()).decode()
        raw_string = f"{base64_encoded}{self.config.cryptomus.API_KEY}"
        return hashlib.md5(raw_string.encode()).hexdigest()
