import logging
import json
import uuid
from aiogram.fsm.storage.redis import RedisStorage
import aiohttp
from sqlalchemy import Transaction
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram import Bot
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiohttp.web import Application, Request, Response
from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.routers.main_menu.handler import redirect_to_main_menu
from app.bot.utils.constants import CRYPTOMUS_WEBHOOK, DEFAULT_LANGUAGE, EVENT_PAYMENT_CANCELED_TAG, EVENT_PAYMENT_SUCCEEDED_TAG, Currency, TransactionStatus
from app.bot.utils.formatting import format_device_count, format_subscription_period
from app.bot.utils.navigation import NavSubscription
from app.bot.utils.payment import generate_signature
from app.bot.models import ServicesContainer, SubscriptionData
from app.config import Config
from app.db.models.user import User

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
        self.app.router.add_post(CRYPTOMUS_WEBHOOK, lambda request: self.webhook_handler(request))
        logger.info("Cryptomus payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        bot_username = (await self.bot.get_me()).username
        redirect_url = f"https://t.me/{bot_username}"
        order_id = str(uuid.uuid4())
        price = str(data.price)

        payload = {
            "merchant_id": self.config.cryptomus.MERCHANT_ID,
            "amount": price,
            "currency": self.currency.code,
            "order_id": order_id,
            "url_success": redirect_url,
            "url_return": redirect_url,
            "url_callback": CRYPTOMUS_WEBHOOK,
        }

        sign = await generate_signature(payload)
        headers = {"merchant": self.config.cryptomus.MERCHANT_ID, "sign": sign, "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.cryptomus.com/v1/payment", json=payload, headers=headers) as response:
                result = await response.json()
                if response.status == 200 and result.get("result", {}).get("url"):
                    pay_url = result["result"]["url"]

        async with self.session() as session:
            await Transaction.create(
                session=session,
                tg_id=data.user_id,
                subscription=data.pack(),
                payment_id=response.id,
                status=TransactionStatus.PENDING,
            )

        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        return pay_url

    async def webhook_handler(self, request: Request) -> Response:
        # используйте список доверенных ip-адресов и разрешайте запросы к url_callback только с наших ip-адресов. Мы отправляем веб-ссылки с ip. 91.227.144.54
        try:
            event_json = await request.json()

            sign = event_json.get("sign")
            if not sign:
                return Response(status=400)

            calculated_sign = await generate_signature(event_json, self.config.cryptomus.API_KEY)
            if sign.lower() != calculated_sign.lower():
                return Response(status=400)
            
            match event_json.get("status"):
                case "paid":
                    payment_info = event_json.get("payment", {})
                    order_id = payment_info.get("order_id")
                    await self.handle_payment_succeeded(order_id)
                case "cancel":
                    await self.handle_payment_canceled(order_id)
                case _:
                    return Response(status=400)

            return Response(status=200)
        except Exception as exception:
            logger.exception(f"Error processing Cryptomus webhook: {exception}")
            return Response(status=400)

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        logger.info(f"Payment succeeded {payment_id}")

        async with self.session() as session:
            transaction = await Transaction.get_by_id(session=session, payment_id=payment_id)
            data = SubscriptionData.unpack(transaction.subscription)
            logger.debug(f"Subscription data unpacked: {data}")
            user = await User.get(session=session, tg_id=data.user_id)

            await Transaction.update(
                session=session,
                payment_id=payment_id,
                status=TransactionStatus.COMPLETED,
            )

        await self.services.notification.notify_developer(
            text=EVENT_PAYMENT_SUCCEEDED_TAG
            + "\n\n"
            + _("payment:event:payment_succeeded").format(
                payment_id=payment_id,
                user_id=user.tg_id,
                devices=format_device_count(data.devices),
                duration=format_subscription_period(data.duration),
            ),
        )

        locale = user.language_code if user else DEFAULT_LANGUAGE
        with self.i18n.use_locale(locale):
            await redirect_to_main_menu(bot=self.bot, user=user, storage=self.storage)

            if data.is_extend:
                await self.services.vpn.extend_subscription(
                    user=user,
                    devices=data.devices,
                    duration=data.duration,
                )
                logger.info(f"Subscription extended for user {user.tg_id}")
                await self.services.notification.notify_extend_success(
                    user_id=user.tg_id,
                    data=data,
                )
            elif data.is_change:
                await self.services.vpn.change_subscription(
                    user=user,
                    devices=data.devices,
                    duration=data.duration,
                )
                logger.info(f"Subscription changed for user {user.tg_id}")
                await self.services.notification.notify_change_success(
                    user_id=user.tg_id,
                    data=data,
                )
            else:
                await self.services.vpn.create_subscription(
                    user=user,
                    devices=data.devices,
                    duration=data.duration,
                )
                logger.info(f"Subscription created for user {user.tg_id}")
                key = await self.services.vpn.get_key(user)
                await self.services.notification.notify_purchase_success(
                    user_id=user.tg_id,
                    key=key,
                )

    async def handle_payment_canceled(self, payment_id: str) -> None:
        logger.info(f"Payment canceled {payment_id}")
        async with self.session() as session:
            transaction = await Transaction.get_by_id(session=session, payment_id=payment_id)
            data = SubscriptionData.unpack(transaction.subscription)

            await Transaction.update(
                session=session,
                payment_id=payment_id,
                status=TransactionStatus.CANCELED,
            )

        await self.services.notification.notify_developer(
            text=EVENT_PAYMENT_CANCELED_TAG
            + "\n\n"
            + _("payment:event:payment_canceled").format(
                payment_id=payment_id,
                user_id=data.user_id,
                devices=format_device_count(data.devices),
                duration=format_subscription_period(data.duration),
            ),
        )
