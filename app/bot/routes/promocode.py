import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import Navigation
from app.bot.services.plans import PlansService
from app.bot.services.promocode import PromocodeService
from app.bot.services.vpn import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class ActivatePromocodeStates(StatesGroup):
    """
    States for activate a promocode.
    """

    waiting_for_promocode = State()


@router.callback_query(F.data == Navigation.PROMOCODE, IsPrivate())
async def callback_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting promocode activation.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        state (FSMContext): The FSM context for storing user state and data.
    """
    logger.info(f"User {callback.from_user.id} started activating promocode.")
    await state.set_state(ActivatePromocodeStates.waiting_for_promocode)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Activate promocode:*\n" "\n" "_Send promocode to activation_"),
        reply_markup=back_keyboard(Navigation.SUBSCRIPTION),
    )


@router.message(ActivatePromocodeStates.waiting_for_promocode, IsPrivate())
async def handle_promocode_input(
    message: Message,
    promocode_service: PromocodeService,
    vpn_service: VPNService,
    state: FSMContext,
) -> None:
    """
    Handles the input of a promocode and activates it if valid.

    Arguments:
        message (Message): The message containing the promocode.
        promocode_service (PromocodeService): Service for managing promocode data.
        vpn_service (VPNService): Service for handling VPN subscriptions.
        state (FSMContext): The FSM context for storing user state and data.
    """
    input_promocode = message.text.strip()
    await message.delete()
    logger.info(f"User {message.from_user.id} entered promocode: {input_promocode} for activating.")

    promocode = await promocode_service.get_promocode(input_promocode)
    if promocode:
        if not promocode.is_activated:
            await vpn_service.activate_promocode(message.from_user.id, promocode)
            message = await state.get_value("message")
            await message.edit_text(
                text=_(
                    "✅ Promocode {promocode} was successfully activated!\n"
                    "\n"
                    "_You have received {traffic} and {duration}._"
                ).format(
                    promocode=input_promocode,
                    traffic=PlansService.convert_traffic_to_title(promocode.traffic),
                    duration=PlansService.convert_days_to_period(promocode.duration),
                ),
                reply_markup=back_keyboard(Navigation.SUBSCRIPTION),
            )
            await state.clear()
            return None

    notification = await message.answer(
        text=_("❌ Promocode is invalid or has already been activated!").format(
            promocode=input_promocode
        )
    )
    await asyncio.sleep(5)
    await notification.delete()
