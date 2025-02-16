import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer, SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.routers.main_menu.handler import redirect_to_main_menu
from app.bot.utils.constants import Currency, CurrencySymbol
from app.bot.utils.formatting import format_device_count, format_subscription_period
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import Transaction, User

logger = logging.getLogger(__name__)


class TelegramStars(PaymentGateway):
    name = ""
    currency = Currency.XTR
    symbol = CurrencySymbol.XTR
    callback = NavSubscription.PAY_TELEGRAM_STARS

    def __init__(
        self,
        config: Config,
        session: async_sessionmaker,
        bot: Bot,
        services: ServicesContainer,
    ):
        self.name = __("payment:gateway:telegram_stars")
        self.config = config
        self.session = session
        self.bot = bot
        self.services = services
        logger.info("TelegramStars payment gateway initialized.")

    async def create_payment(self, data: SubscriptionData) -> str:
        prices = [LabeledPrice(label=self.currency.value, amount=1)]
        # prices = [LabeledPrice(label=self.currency.value, amount=data.price)]
        devices = format_device_count(data.devices)
        duration = format_subscription_period(data.duration)
        title = _("payment:invoice:title").format(devices=devices, duration=duration)
        description = _("payment:invoice:description").format(devices=devices, duration=duration)
        pay_url = await self.bot.create_invoice_link(
            title=title,
            description=description,
            prices=prices,
            payload=data.pack(),
            currency=self.currency.value,
        )
        logger.info(f"Payment link created for user {data.user_id}: {pay_url}")
        return pay_url

    async def handle_payment_succeeded(self, payment_id: str, state: FSMContext) -> None:
        logger.info(f"Payment succeeded {payment_id}")

        async with self.session() as session:
            transaction = await Transaction.get_by_id(session=session, payment_id=payment_id)
            data = SubscriptionData.unpack(transaction.subscription)
            logger.debug(f"Subscription data unpacked: {data}")
            user = await User.get(session=session, tg_id=data.user_id)

        await redirect_to_main_menu(bot=self.bot, user=user, state=state)

        if data.is_extend:
            await self.services.vpn.extend_subscription(
                user=user,
                devices=data.devices,
                duration=data.duration,
            )
            logger.info(f"Subscription extented for user {user.tg_id}")
            await self.services.notification.notify_extend_success(user_id=user.tg_id, data=data)
        elif data.is_change:
            await self.services.vpn.change_subscription(
                user=user,
                devices=data.devices,
                duration=data.duration,
            )
            logger.info(f"Subscription changed for user {user.tg_id}")
            await self.services.notification.notify_change_success(user_id=user.tg_id, data=data)
        else:
            await self.services.vpn.create_subscription(
                user=user,
                devices=data.devices,
                duration=data.duration,
            )
            logger.info(f"Subscription created for user {user.tg_id}")
            key = await self.services.vpn.get_key(user)
            await self.services.notification.notify_purchase_success(user_id=user.tg_id, key=key)

    async def handle_payment_canceled(self, payment_id: str) -> None:
        logger.info(f"Payment canceled {payment_id}")
        pass
