import logging

from aiogram import Bot
from aiogram.utils.i18n import gettext as _
from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy.ext.asyncio import AsyncSession
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

from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.routes.subscription.keyboard import payment_success_keyboard
from app.bot.routes.utils.keyboard import back_to_main_menu_keyboard
from app.bot.services.plan import PlanService
from app.bot.services.vpn import VPNService
from app.config import Config
from app.db.models.transaction import Transaction

logger = logging.getLogger(__name__)


class Yookassa(PaymentGateway):
    """
    Service for creating payments through the Yookassa platform.
    """

    name = "YooKassa"
    symbol = "₽"
    code = Currency.RUB
    callback = NavSubscription.PAY_YOOKASSA

    def __init__(self, config: Config, bot: Bot):
        """
        Initialize the Yookassa service with shop credentials.

        Arguments:
            config (Config): Configuration instance.
            bot (Bot): Telegram Bot instance.
        """
        self.config = config
        self.bot = bot
        Configuration.configure(config.yookassa.SHOP_ID, config.yookassa.TOKEN)

    async def create_payment(self, session: AsyncSession, data: SubscriptionData) -> str:
        """
        Create a payment link for the subscription using Yookassa.

        This method generates a payment link based on the provided subscription data,
        including devices and duration.

        Arguments:
            data (SubscriptionData): The subscription data, including devices and duration.

        Returns:
            str: The payment link for the subscription.
        """
        redirect = f"https://t.me/{(await self.bot.get_me()).username}"
        description = _("Subscription | {devices} for {duration}").format(
            devices=data.devices, duration=data.duration
        )

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

        async with session() as session:
            await Transaction.create(
                session=session,
                user_id=data.user_id,
                plan=data.pack(),
                payment_id=response.id,
                amount=data.price,
                status="process",
            )

        return response.confirmation["confirmation_url"]

    def set_webhook(self, url: str) -> None:  # Only for partners api
        """
        Set a webhook for the Yookassa platform.

        This method registers a webhook for payment notifications from Yookassa.
        It is only available for partners API.

        Arguments:
            url (str): The URL to register for webhook notifications.
        """
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

    @staticmethod
    async def webhook_handler(request: Request, session, bot: Bot, vpn_service: VPNService):
        """
        Handles incoming Yookassa webhook notifications.

        This method processes payment status updates from Yookassa and updates
        the status of the corresponding subscription.

        Arguments:
            request (Request): The incoming webhook request.

        Returns:
            web.Response: The response indicating the result of the processing.
        """
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
                    some_data = {
                        "paymentId": response_object.id,
                        "paymentStatus": response_object.status,
                    }
                # case WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE:
                #     logger.debug("PAYMENT_WAITING_FOR_CAPTURE")
                #     some_data = {
                #         "paymentId": response_object.id,
                #         "paymentStatus": response_object.status,
                #     }
                # case WebhookNotificationEventType.PAYMENT_CANCELED:
                #     logger.debug("PAYMENT_CANCELED")
                #     some_data = {
                #         "paymentId": response_object.id,
                #         "paymentStatus": response_object.status,
                #     }
                case _:
                    return web.Response(status=400)

            payment_info = Payment.find_one(some_data["paymentId"])
            if payment_info:
                payment_status = payment_info.status
                print(payment_status)

                async with session() as session:
                    transaction = await Transaction.get(session=session, payment_id=payment_info.id)
                data = SubscriptionData.unpack(transaction.plan)
                await bot.delete_message(chat_id=data.user_id, message_id=data.message_id)
                if data.is_extend:
                    await vpn_service.extend_subscription(data.user_id, data.devices, data.duration)
                    logger.info(f"Subscription extented for user {data.user_id}")
                else:
                    await vpn_service.create_subscription(data.user_id, data.devices, data.duration)
                    logger.info(f"Subscription created for user {data.user_id}")

                await Transaction.update(
                    session=session,
                    user_id=data.user_id,
                    plan=data.pack(),
                    payment_id=payment_info.id,
                    amount=data.price,
                    status="success",
                )

                if data.is_extend:
                    await bot.send_message(
                        chat_id=data.user_id,
                        text=_(
                            "✅ *Payment successful!*\n"
                            "\n"
                            "Your subscription has been extended for {duration}\n"
                        ).format(duration=PlanService.convert_days_to_period(data.duration)),
                        message_effect_id="5046509860389126442",
                        reply_markup=back_to_main_menu_keyboard(),
                    )
                else:
                    key = await vpn_service.get_key(data.user_id)
                    await bot.send_message(
                        chat_id=data.user_id,
                        text=_(
                            "✅ *Payment successful!*\n"
                            "\n"
                            "🔑 *Your key:* ```{key}```\n"
                            "_The key will be saved in your profile._\n"
                            "\n"
                            "To start using our service, go to the download page of the application and "
                            "download it for your platform. Then you can manually enter the key or click "
                            "`🔌 Connect` and the key will be automatically added to the application."
                        ).format(key=key),
                        message_effect_id="5046509860389126442",  # TODO: Delete effect
                        reply_markup=payment_success_keyboard(),
                    )
            else:
                return web.Response(status=400)

        except Exception as exception:
            print(exception)
            return web.Response(status=400)

        return web.Response(status=200)
