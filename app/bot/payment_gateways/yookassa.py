import logging

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from aiohttp.web import Application, Request, Response
from sqlalchemy.ext.asyncio import async_sessionmaker
from yookassa import Configuration, Payment
from yookassa.domain.common import SecurityHelper
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.receipt import Receipt, ReceiptItem
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)
from yookassa.domain.request.payment_request import PaymentRequest

from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.utils.constants import YOOKASSA_WEBHOOK, Currency, TransactionStatus
from app.bot.utils.formatting import format_device_count, format_subscription_period
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import Transaction

logger = logging.getLogger(__name__)


class Yookassa(PaymentGateway):
    name = ""
    currency = Currency.RUB
    callback = NavSubscription.PAY_YOOKASSA

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
        self.name = __("payment:gateway:yookassa")
        self.app = app
        self.config = config
        self.session = session
        self.storage = storage
        self.bot = bot
        self.i18n = i18n
        self.services = services

        Configuration.configure(self.config.yookassa.SHOP_ID, self.config.yookassa.TOKEN)
        self.app.router.add_post(YOOKASSA_WEBHOOK, self.webhook_handler)
        logger.info("YooKassa payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        bot_username = (await self.bot.get_me()).username
        redirect_url = f"https://t.me/{bot_username}"

        description = _("payment:invoice:description").format(
            devices=format_device_count(data.devices),
            duration=format_subscription_period(data.duration),
        )

        price = str(data.price)

        receipt = Receipt(
            customer={"email": self.config.shop.EMAIL},
            items=[
                ReceiptItem(
                    description=description,
                    quantity=1,
                    amount={"value": price, "currency": self.currency.code},
                    vat_code=1,
                )
            ],
        )

        request = PaymentRequest(
            amount={"value": price, "currency": self.currency.code},
            confirmation={"type": ConfirmationType.REDIRECT, "return_url": redirect_url},
            capture=True,
            save_payment_method=False,
            description=description,
            receipt=receipt,
        )

        response = Payment.create(request)

        async with self.session() as session:
            await Transaction.create(
                session=session,
                tg_id=data.user_id,
                subscription=data.pack(),
                payment_id=response.id,
                status=TransactionStatus.PENDING,
            )

        pay_url = response.confirmation["confirmation_url"]
        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        return pay_url

    async def handle_payment_succeeded(self, payment_id: str) -> None:
        await self._on_payment_succeeded(payment_id)

    async def handle_payment_canceled(self, payment_id: str) -> None:
        await self._on_payment_canceled(payment_id)

    async def webhook_handler(self, request: Request) -> Response:
        ip = request.headers.get("X-Forwarded-For", request.remote)

        if not SecurityHelper().is_ip_trusted(ip):
            return Response(status=403)

        try:
            event_json = await request.json()
            notification_object = WebhookNotificationFactory().create(event_json)
            response_object = notification_object.object
            payment_id = response_object.id

            match notification_object.event:
                case WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                    await self.handle_payment_succeeded(payment_id)
                    return Response(status=200)

                case WebhookNotificationEventType.PAYMENT_CANCELED:
                    await self.handle_payment_canceled(payment_id)
                    return Response(status=200)

                case _:
                    return Response(status=400)

        except Exception as exception:
            logger.exception(f"Error processing YooKassa webhook: {exception}")
            return Response(status=400)
