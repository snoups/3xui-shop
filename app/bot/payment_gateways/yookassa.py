import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import gettext as _
from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from yookassa import Configuration, Payment, Webhook
from yookassa.domain.common import SecurityHelper
from yookassa.domain.common.confirmation_type import ConfirmationType
from yookassa.domain.models.currency import Currency
from yookassa.domain.models.receipt import Receipt, ReceiptItem
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)
from yookassa.domain.request.payment_request_builder import PaymentRequestBuilder

from app.bot.models import SubscriptionData
from app.bot.models.enums import TransactionStatus
from app.bot.payment_gateways import PaymentGateway
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.services.plan import PlanService
from app.bot.services.vpn import VPNService
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import Transaction, User

logger = logging.getLogger(__name__)


class Yookassa(PaymentGateway):
    name = "YooKassa"
    symbol = "₽"
    code = Currency.RUB
    callback = NavSubscription.PAY_YOOKASSA

    def __init__(
        self,
        config: Config,
        bot: Bot,
        session: async_sessionmaker,
        storage: RedisStorage,
        vpn_service: VPNService,
    ):
        self.config = config
        self.bot = bot
        self.session = session
        self.storage = storage
        self.vpn_service = vpn_service

        Configuration.configure(config.yookassa.SHOP_ID, config.yookassa.TOKEN)
        logger.info("YooKassa payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        redirect = f"https://t.me/{(await self.bot.get_me()).username}"
        devices = PlanService.convert_devices_to_title(data.devices)
        duration = PlanService.convert_days_to_period(data.duration)
        description = _("payment:invoice:description").format(devices=devices, duration=duration)

        receipt = Receipt()
        receipt.customer = {"email": self.config.bot.EMAIL}
        receipt.items = [
            ReceiptItem(
                {
                    "description": description,
                    "quantity": 1,
                    "amount": {"value": str(data.price), "currency": self.code},
                    "vat_code": 1,
                }
            )
        ]

        builder = PaymentRequestBuilder()
        builder.set_amount({"value": str(data.price), "currency": self.code})
        builder.set_confirmation({"type": ConfirmationType.REDIRECT, "return_url": redirect})
        builder.set_capture(True)
        builder.set_save_payment_method(False)
        builder.set_description(description)
        builder.set_receipt(receipt)

        request = builder.build()
        response = Payment.create(request)

        async with self.session() as session:
            await Transaction.create(
                session=session,
                tg_id=data.user_id,
                subscription=data.pack(),
                payment_id=response.id,
                status=TransactionStatus.PENDING,
            )

        return response.confirmation["confirmation_url"]

    def set_webhook(self, url: str) -> None:
        try:
            events = [
                WebhookNotificationEventType.PAYMENT_SUCCEEDED,
                # WebhookNotificationEventType.PAYMENT_CANCELED,
            ]
            webhook_list = Webhook.list()

            for event in events:
                is_set = False
                for webhook in webhook_list.items:
                    if webhook.event != event:
                        continue
                    if webhook.url != url:
                        Webhook.remove(webhook.id)
                    else:
                        is_set = True

                if not is_set:
                    response = Webhook.add({"event": event, "url": url})
                    logger.info(f"Webhook registered successfully: {response}")
        except Exception as exception:
            logger.debug(f"Failed to register webhook: {exception}")

    async def webhook_handler(self, request: Request):
        ip = request.headers.get("X-Forwarded-For", request.remote)
        if not SecurityHelper().is_ip_trusted(ip):
            return web.Response(status=403)

        event_json = await request.json()
        try:
            notification_object = WebhookNotificationFactory().create(event_json)
            response_object = notification_object.object

            match notification_object.event:
                case WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                    logger.debug("PAYMENT_SUCCEEDED")
                    payment_id = response_object.id

                    async with self.session() as session:
                        transaction = await Transaction.get(session=session, payment_id=payment_id)
                        data = SubscriptionData.unpack(transaction.subscription)
                        user = await User.get(session=session, tg_id=data.user_id)
                        await Transaction.update(
                            session=session,
                            tg_id=data.user_id,
                            subscription=data.pack(),
                            payment_id=payment_id,
                            status=TransactionStatus.COMPLETED,
                        )

                    try:
                        state: FSMContext = FSMContext(
                            storage=self.storage,
                            key=StorageKey(
                                chat_id=data.user_id,
                                user_id=data.user_id,
                                bot_id=self.bot.id,
                            ),
                        )
                        message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
                        await self.bot.delete_message(chat_id=data.user_id, message_id=message_id)
                    except Exception as exception:
                        logger.debug(f"Failed to delete message: {exception}")
                    if data.is_extend:
                        await self.vpn_service.extend_subscription(
                            user, data.devices, data.duration
                        )
                        logger.info(f"Subscription extented for user {data.user_id}")
                    else:
                        await self.vpn_service.create_subscription(
                            user, data.devices, data.duration
                        )
                        logger.info(f"Subscription created for user {data.user_id}")

                    if data.is_extend:
                        await self.bot.send_message(
                            chat_id=data.user_id,
                            text=_("payment:message:extend_success").format(
                                duration=PlanService.convert_days_to_period(data.duration)
                            ),
                            message_effect_id="5046509860389126442",
                            reply_markup=back_keyboard(NavSubscription.MAIN),
                        )
                    else:
                        from app.bot.routers.subscription.keyboard import (
                            payment_success_keyboard,
                        )

                        key = await self.vpn_service.get_key(user)
                        await self.bot.send_message(
                            chat_id=data.user_id,
                            text=_("payment:message:buying_success").format(key=key),
                            message_effect_id="5046509860389126442",  # TODO: Delete effect
                            reply_markup=payment_success_keyboard(),
                        )
                    return web.Response(status=200)
                case WebhookNotificationEventType.PAYMENT_CANCELED:
                    logger.debug("PAYMENT_CANCELED")
                    payment_id = response_object.id

                    async with self.session() as session:
                        transaction = await Transaction.get(session=session, payment_id=payment_id)
                        data = SubscriptionData.unpack(transaction.subscription)
                        await Transaction.update(
                            session=session,
                            tg_id=data.user_id,
                            subscription=data.pack(),
                            payment_id=payment_id,
                            status=TransactionStatus.CANCELED,
                        )

                    return web.Response(status=200)
                case _:
                    return web.Response(status=400)

        except Exception as exception:
            print(exception)
            return web.Response(status=400)
