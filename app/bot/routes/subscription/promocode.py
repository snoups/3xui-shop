import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import NavSubscription
from app.bot.services import (
    NotificationService,
    PlanService,
    PromocodeService,
    VPNService,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class ActivatePromocodeStates(StatesGroup):
    """
    States for activate a promocode.
    """

    promocode_input = State()


@router.callback_query(F.data == NavSubscription.PROMOCODE, IsPrivate())
async def callback_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting promocode activation.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        state (FSMContext): The FSM context for storing user state and data.
    """
    logger.info(f"User {callback.from_user.id} started activating promocode.")
    await state.set_state(ActivatePromocodeStates.promocode_input)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Activate promocode:*\n" "\n" "_Send promocode to activation_"),
        reply_markup=back_keyboard(NavSubscription.MAIN),
    )


@router.message(ActivatePromocodeStates.promocode_input, IsPrivate())
async def handle_promocode_input(
    message: Message,
    state: FSMContext,
    promocode_service: PromocodeService,
    vpn_service: VPNService,
) -> None:
    """
    Handles the input of a promocode and activates it if valid.

    Arguments:
        message (Message): The message containing the promocode.
        state (FSMContext): The FSM context for storing user state and data.
        promocode_service (PromocodeService): Service for managing promocode data.
        vpn_service (VPNService): Service for handling VPN subscriptions.
    """
    input_promocode = message.text.strip()
    logger.info(f"User {message.from_user.id} entered promocode: {input_promocode} for activating.")

    promocode = await promocode_service.get_promocode(input_promocode)
    if promocode and not promocode.is_activated:
        success = await vpn_service.activate_promocode(message.from_user.id, promocode)
        message = await state.get_value("message")
        if success:
            await message.edit_text(
                text=_(
                    "✅ Promocode {promocode} was successfully activated!\n"
                    "\n"
                    "_You have received {duration} to your subscription._"
                ).format(
                    promocode=input_promocode,
                    duration=PlanService.convert_days_to_period(promocode.duration),
                ),
                reply_markup=back_keyboard(NavSubscription.MAIN),
            )
        else:
            await message.edit_text(
                text=_(
                    "❌ Failed to activate promocode {promocode}, please try again later."
                ).format(
                    promocode=input_promocode,
                ),
                reply_markup=back_keyboard(NavSubscription.MAIN),
            )
        await state.set_state(None)
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Promocode is invalid or has already been activated!").format(
                promocode=input_promocode
            ),
            duration=5,
        )
