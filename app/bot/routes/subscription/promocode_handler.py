import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavSubscription
from app.bot.routes.utils.keyboard import back_keyboard
from app.bot.services import (
    NotificationService,
    PlanService,
    PromocodeService,
    VPNService,
)
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class ActivatePromocodeStates(StatesGroup):
    promocode_input = State()


@router.callback_query(F.data == NavSubscription.PROMOCODE)
async def callback_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"User {user.tg_id} started activating promocode.")
    await state.set_state(ActivatePromocodeStates.promocode_input)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Activate promocode:*\n" "\n" "_Send promocode to activation_"),
        reply_markup=back_keyboard(NavSubscription.MAIN),
    )


@router.message(ActivatePromocodeStates.promocode_input)
async def handle_promocode_input(
    message: Message,
    user: User,
    state: FSMContext,
    promocode_service: PromocodeService,
    vpn_service: VPNService,
) -> None:
    input_promocode = message.text.strip()
    logger.info(f"User {user.tg_id} entered promocode: {input_promocode} for activating.")

    promocode = await promocode_service.get_promocode(input_promocode)
    if promocode and not promocode.is_activated:
        success = await vpn_service.activate_promocode(user.tg_id, promocode)
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
