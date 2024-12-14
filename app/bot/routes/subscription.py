import json
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _
from py3xui import AsyncApi
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.is_private import IsPrivate
from app.bot.keyboards.pay import pay_keyboard
from app.bot.keyboards.payment_method import payment_method_keyboard
from app.bot.keyboards.subscription import duration_keyboard, traffic_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services import payment_service, subscription_service

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_choosing_traffic(callback: CallbackQuery) -> None:
    """
    Sends a message prompting the user to select the traffic volume for the subscription.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
    """
    text = _("🌐 Select the traffic volume:")
    await callback.message.answer(text, reply_markup=traffic_keyboard())


async def show_choosing_duration(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Sends a message prompting the user to select the subscription duration based on their plan.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    selected_plan = await subscription_service.get_selected_plan(state)
    await callback.message.answer(
        _("⏳ Specify the duration:"),
        reply_markup=duration_keyboard(selected_plan["prices"]),
    )


async def show_choosing_payment_method(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Sends a message prompting the user to choose a payment method for their subscription.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    selected_plan = await subscription_service.get_selected_plan(state)
    selected_duration = await subscription_service.get_selected_duration(state)
    await callback.message.answer(
        _("💳 Choose a payment method:"),
        reply_markup=payment_method_keyboard(selected_plan["prices"], selected_duration),
    )


@router.callback_query(F.data == NavigationAction.SUBSCRIPTION, IsPrivate())
async def callback_subscription(callback: CallbackQuery) -> None:
    """
    Handles the subscription initiation by sending the traffic selection prompt.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    logger.info(f"User {callback.from_user.id} started subscription process.")
    await callback.message.delete()
    await show_choosing_traffic(callback)


@router.callback_query(F.data.startswith(NavigationAction.TRAFFIC), IsPrivate())
async def callback_choosing_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the selection of a traffic plan and proceeds to duration selection.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} selected plan: {callback.data}")
    await subscription_service.set_selected_plan(state, callback.data)
    await show_choosing_duration(callback, state)


@router.callback_query(F.data == NavigationAction.BACK_TO_DURATION, IsPrivate())
async def callback_back_to_duration(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the case where the user returns to the duration selection step.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} returned to choosing duration.")
    await show_choosing_duration(callback, state)


@router.callback_query(F.data.startswith(NavigationAction.DURATION), IsPrivate())
async def callback_choosing_duration(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the selection of subscription duration and proceeds to payment method selection.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} selected duration: {callback.data}")
    await subscription_service.set_selected_duration(state, callback.data)
    await show_choosing_payment_method(callback, state)


@router.callback_query(F.data == NavigationAction.BACK_TO_PAYMENT, IsPrivate())
async def callback_back_to_payment(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the case where the user returns to the payment method selection step.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()
    logger.info(f"User {callback.from_user.id} returned to choosing payment method.")
    await show_choosing_payment_method(callback, state)


@router.callback_query(F.data.startswith(NavigationAction.PAY), IsPrivate())
async def callback_choosing_payment_method(
    callback: CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    """
    Handles the payment method selection and displays payment information to the user.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        state (FSMContext): The state of the Finite State Machine (FSM) for the user.
    """
    await callback.message.delete()

    selected_plan = await subscription_service.get_selected_plan(state)
    selected_duration = await subscription_service.get_selected_duration(state)
    logger.info(f"User {callback.from_user.id} selected payment method: {callback.data}")
    logger.info(f"User {callback.from_user.id} selected plan: {selected_plan} {selected_duration}")

    plan = subscription_service.convert_traffic_to_title(selected_plan["traffic"])
    duration = subscription_service.convert_days_to_period(selected_duration)
    payment_method = payment_service.get_payment_method(callback.data)
    price = subscription_service.get_price_for_duration(
        selected_plan["prices"],
        selected_duration,
        payment_method.code,
    )

    data = {
        "user_id": callback.from_user.id,
        "traffic": selected_plan["traffic"],
        "duration": selected_duration,
        "price": price,
    }

    link = await payment_service.create_payment(payment_method, data, bot)

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
            plan=plan,
            duration=duration,
            price=price,
            currency=payment_method.symbol,
        ),
        reply_markup=pay_keyboard(link),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery, bot: Bot, api: AsyncApi, session: AsyncSession
) -> None:
    logger.info("pre_checkout_handler")
    data = json.loads(pre_checkout_query.invoice_payload)
    print(data)
    await subscription_service.create_subscription(session, api, data)
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(
    message: Message, bot: Bot, api: AsyncApi, session: AsyncSession
) -> None:
    logger.info("successful_payment")

    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer(
        f"Your transaction id: {message.successful_payment.telegram_payment_charge_id}"
    )
    # await subscription_service.create_subscription(session, api, message.from_user.id)
