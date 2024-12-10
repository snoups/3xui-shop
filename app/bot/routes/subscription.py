import logging

from aiogram import F, Router
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters.is_private import IsPrivate
from app.bot.keyboards.pay import pay_keyboard
from app.bot.keyboards.payment_method import payment_method_keyboard
from app.bot.keyboards.subscription import duration_keyboard, traffic_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services import subscription_service

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class SubscriptionForm(StatesGroup):
    """
    States for managing the subscription flow.

    Attributes:
        choosing_plan (State): The state where the user selects a traffic plan.
        choosing_duration (State): The state where the user selects the subscription duration.
        choosing_payment_method (State): The state where the user selects a payment method.
    """

    choosing_plan = State()
    choosing_duration = State()
    choosing_payment_method = State()


@router.callback_query(F.data == NavigationAction.SUBSCRIPTION, IsPrivate())
async def callback_subscription(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Starts the subscription process by showing available traffic plans.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()

    text = _("🌐 Select the traffic volume:")
    logger.info(f"User {callback.from_user.id} started subscription process.")

    await callback.message.answer(text, reply_markup=traffic_keyboard())
    await state.set_state(SubscriptionForm.choosing_plan)


# TODO: BUG is accounted for by any callback
@router.callback_query(SubscriptionForm.choosing_plan, IsPrivate())
@router.callback_query(F.data == NavigationAction.BACK_TO_DURATION, IsPrivate())
async def callback_choosing_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles traffic plan selection and moves to duration selection.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()

    if callback.data != NavigationAction.BACK_TO_DURATION:
        await subscription_service.set_selected_plan(state, callback.data)
        logger.info(f"User {callback.from_user.id} selected plan: {callback.data}")
    else:
        logger.info(f"User {callback.from_user.id} returned to choosing duration.")

    selected_plan = await subscription_service.get_selected_plan(state)

    await callback.message.answer(
        _("⏳ Specify the duration:"),
        reply_markup=duration_keyboard(selected_plan["price"]["RUB"]),
    )
    await state.set_state(SubscriptionForm.choosing_duration)


@router.callback_query(SubscriptionForm.choosing_duration, IsPrivate())
@router.callback_query(F.data == NavigationAction.BACK_TO_PAYMENT, IsPrivate())
async def callback_choosing_duration(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles duration selection and moves to payment method selection.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()

    if callback.data != NavigationAction.BACK_TO_PAYMENT:
        await subscription_service.set_selected_duration(state, callback.data)
        logger.info(f"User {callback.from_user.id} selected duration: {callback.data}")
    else:
        logger.info(f"User {callback.from_user.id} returned to choosing payment method.")

    selected_plan = await subscription_service.get_selected_plan(state)
    selected_duration = await subscription_service.get_selected_duration(state)

    await callback.message.answer(
        _("💳 Choose a payment method:"),
        reply_markup=payment_method_keyboard(selected_plan, selected_duration["coefficient"]),
    )
    await state.set_state(SubscriptionForm.choosing_payment_method)


@router.callback_query(
    SubscriptionForm.choosing_payment_method,
    F.data.startswith(NavigationAction.PAY),
    IsPrivate(),
)
async def callback_choosing_payment_method(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles payment method selection and shows subscription details.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()

    selected_plan = await subscription_service.get_selected_plan(state)
    selected_duration = await subscription_service.get_selected_duration(state)
    duration = subscription_service.convert_days_to_period(selected_duration["duration"])

    logger.info(f"User {callback.from_user.id} selected payment method: {callback.data}")
    logger.info(f"User {callback.from_user.id} selected plan: {selected_plan} {selected_duration}")

    if callback.data == NavigationAction.PAY_YOOKASSA:
        currency = "₽"
        price = subscription_service.calculate_price(
            selected_plan["price"]["RUB"],
            selected_duration["coefficient"],
        )
    elif callback.data == NavigationAction.PAY_TELEGRAM_STARS:
        currency = "★"
        price = subscription_service.calculate_price(
            selected_plan["price"]["XTR"],
            selected_duration["coefficient"],
        )
    elif callback.data == NavigationAction.PAY_CRYPTOMUS:
        currency = "$"
        price = subscription_service.calculate_price(
            selected_plan["price"]["USD"],
            selected_duration["coefficient"],
        )
    else:
        currency = "NONE"
        price = "NONE"

    await callback.message.answer(
        _(
            "✅ You selected:\n"
            "\n"
            "Plan: {plan} GB\n"
            "Duration: {duration}\n"
            "Price: {price} {currency}\n"
            "\n"
            "After payment, a unique key will be generated for you, to connect to the VPN."
        ).format(
            plan=selected_plan["traffic"],
            duration=duration,
            price=price,
            currency=currency,
        ),
        reply_markup=pay_keyboard("https://telegram.org/"),
    )
    await callback.answer()
