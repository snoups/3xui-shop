import json
import logging

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.pay import pay_keyboard
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.payment import PaymentService
from app.bot.services.plans import PlansService
from app.bot.services.vpn import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(SubscriptionCallback.filter(F.state.startswith(Navigation.PAY)), IsPrivate())
async def callback_payment_method_selected(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
    bot: Bot,
) -> None:
    logger.info(f"User {callback.from_user.id} selected payment method: {callback.data}")

    traffic = callback_data.traffic
    duration = callback_data.duration
    prices = plans_service.get_plan(traffic).prices.to_dict()

    logger.info(f"User {callback.from_user.id} selected {traffic} GB and {duration} days.")

    payment_service = PaymentService(callback_data.state)
    price = plans_service.get_price_for_duration(
        prices,
        duration,
        payment_service.method.code,
    )
    data = {
        "user_id": callback.from_user.id,
        "traffic": traffic,
        "duration": duration,
        "price": price,
    }

    # TODO: Make a check for the existence of a subscription

    link = await payment_service.create_payment(data, bot)

    await callback.message.edit_text(
        _(
            "✅ *You selected:*\n"
            "\n"
            "Plan: {plan}\n"
            "Duration: {duration}\n"
            "Price: {price} {currency}\n"
            "\n"
            "_After payment, a unique key will be generated for you, to connect to the VPN. "
            "The key will be available in your profile._"
        ).format(
            plan=plans_service.convert_traffic_to_title(traffic),
            duration=plans_service.convert_days_to_period(duration),
            price=price,
            currency=payment_service.method.symbol,
        ),
        reply_markup=pay_keyboard(link, callback_data),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery, vpn_service: VPNService
) -> None:
    logger.info("pre_checkout_handler")
    data = json.loads(pre_checkout_query.invoice_payload)
    logger.info(data)
    await vpn_service.create_subscription(data["user_id"], data["traffic"], data["duration"])
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot) -> None:
    logger.info("successful_payment")
    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer(
        f"*Your transaction id*: ```{message.successful_payment.telegram_payment_charge_id}```"
    )
