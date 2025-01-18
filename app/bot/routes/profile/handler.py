import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavProfile
from app.bot.services import ClientData, VPNService

from .keyboard import buy_subscription_keyboard, profile_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def prepare_message(user: User, client_data: ClientData) -> str:
    profile = (
        _("👤 *Your profile:*\n" "Name: {name}\n" "ID: {id}\n").format(
            name=user.first_name, id=user.id
        )
        + "\n"
    )

    if not client_data:
        subscription = _(
            "_You don't have a subscription yet. "
            "To purchase one, go to the subscription page by clicking the button below._"
        )
        return profile + subscription

    subscription = _("📅 *Subscription:*\n" "Devices: {devices}\n").format(
        devices=client_data.max_devices
    )
    subscription += (
        _("_Subscription period has expired._\n")
        if client_data.has_subscription_expired
        else _("Expires in: {expiry_time}\n").format(expiry_time=client_data.expiry_time)
    )
    subscription += "\n"

    statistics = _(
        "📊 *Statistics:*\n" "Total: {total}\n" "Uploaded: ↑ {up}\n" "Downloaded: ↓ {down}"
    ).format(
        total=client_data.traffic_used,
        up=client_data.traffic_up,
        down=client_data.traffic_down,
    )

    return profile + subscription + statistics


@router.callback_query(F.data == NavProfile.MAIN)
async def callback_profile(
    callback: CallbackQuery,
    vpn_service: VPNService,
    state: FSMContext,
) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} opened profile page.")
    await state.update_data(callback=NavProfile.MAIN)
    client_data = await vpn_service.get_client_data(user.id)
    reply_markup = (
        profile_keyboard()
        if client_data and not client_data.has_subscription_expired
        else buy_subscription_keyboard()
    )
    await callback.message.edit_text(
        text=await prepare_message(user, client_data),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == NavProfile.SHOW_KEY)
async def callback_show_key(callback: CallbackQuery, vpn_service: VPNService) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} looked key.")
    key = await vpn_service.get_key(user.id)
    key_text = _("🔑 *Your key:* (Closes after {seconds_text}) ```{key}```")
    message = await callback.message.answer(key_text.format(key=key, seconds_text=_("6 seconds")))

    for seconds in range(5, 0, -1):
        seconds_text = _("1 second", "{} seconds", seconds).format(seconds)
        await asyncio.sleep(1)
        await message.edit_text(text=key_text.format(key=key, seconds_text=seconds_text))
    await message.delete()
