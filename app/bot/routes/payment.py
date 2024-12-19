import json
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsPrivate
from app.bot.keyboards.pay import pay_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services.payment import PaymentService
from app.bot.services.subscription import SubscriptionService
from app.bot.services.vpn import VPNService
from app.db.models.user import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data.startswith(NavigationAction.PAY), IsPrivate())
async def callback_choosing_payment_method(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    subscription: SubscriptionService,
) -> None:
    """
    Handles the payment method selection and displays payment information to the user.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The user's FSM state.
        bot (Bot): The bot instance.
        subscription (SubscriptionService): The subscription service instance.
    """
    logger.info(f"User {callback.from_user.id} selected payment method: {callback.data}")
    await callback.message.delete()

    # extend = await state.get_value("extend")
    # if extend:
    #     pass

    plan_callback = await state.get_value("plan_callback")
    duration_callback = await state.get_value("duration_callback")
    plan = subscription.get_plan(plan_callback)
    duration = subscription.get_duration(duration_callback)

    logger.info(f"User {callback.from_user.id} selected plan: {plan} {duration}")

    payment_service = PaymentService(callback.data)
    price = subscription.get_price_for_duration(
        plan["prices"],
        duration,
        payment_service.method.code,
    )

    data = {
        "user_id": callback.from_user.id,
        "traffic": plan["traffic"],
        "duration": duration,
        "price": price,
    }

    link = await payment_service.create_payment(data, bot)

    await callback.message.answer(
        _(
            "✅ You selected:\n"
            "\n"
            "Plan: {plan}\n"
            "Duration: {duration}\n"
            "Price: {price} {currency}\n"
            "\n"
            "After payment, a unique key will be generated for you, to connect to the VPN."
        ).format(
            plan=subscription.convert_traffic_to_title(plan["traffic"]),
            duration=subscription.convert_days_to_period(duration),
            price=price,
            currency=payment_service.method.symbol,
        ),
        reply_markup=pay_keyboard(link),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery,
    session: AsyncSession,
    subscription: SubscriptionService,
    vpn: VPNService,
) -> None:
    """
    Handles the pre-checkout query before the user proceeds with payment.

    Arguments:
        pre_checkout_query (PreCheckoutQuery): The pre-checkout query from Telegram.
        session (AsyncSession): Database session for managing user data.
        subscription (SubscriptionService): The subscription service instance.
        vpn (VPNService): The VPN service instance.
    """
    logger.info("pre_checkout_handler")
    data = json.loads(pre_checkout_query.invoice_payload)
    logger.info(data)

    user: User = await User.get(session, user_id=data["user_id"])
    await subscription.create_subscription(vpn, user, data["traffic"], data["duration"])
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot) -> None:
    """
    Handles the successful payment notification from Telegram.

    Arguments:
        message (Message): The message containing payment details.
        bot (Bot): The bot instance.
    """
    logger.info("successful_payment")
    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer(
        f"Your transaction id: {message.successful_payment.telegram_payment_charge_id}"
    )
