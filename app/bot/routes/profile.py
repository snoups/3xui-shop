import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types import User as TelegramUser
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.profile import buy_subscription_keyboard, show_key_keyboard
from app.bot.navigation import Navigation
from app.bot.services import ClientService, VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def prepare_message(user: TelegramUser, client: ClientService) -> str:
    """
    Prepares the user's profile message, including subscription and statistics details.

    Arguments:
        user (User): The user for whom the profile message is being prepared.
        client (ClientService): The client service to retrieve subscription and statistics.

    Returns:
        str: A formatted message with the user's profile, subscription, and statistics.
    """
    header_text = _("👤 *Your profile:*\n" "Name: {name}\n" "ID: {id}\n").format(
        name=user.first_name, id=user.id
    )
    header_text += "\n"

    if not client:
        no_subscription_text = _(
            "_You don't have a subscription yet. "
            "To purchase one, go to the subscription page by clicking the button below._"
        )
        return header_text + no_subscription_text

    subscription_text = _("📅 *Subscription:*\n" "Devices: {devices}\n").format(
        devices=client.max_devices
    )

    if client.has_subscription_expired:
        subscription_text += _("_Subscription period has expired._\n")
    else:
        subscription_text += _("Expires in: {expiry_time}\n").format(
            expiry_time=client.expiry_time,
        )

    subscription_text += "\n"

    statistics_text = _(
        "📊 *Statistics:*\n" "Total: {total}\n" "Uploaded: ↑ {up}\n" "Downloaded: ↓ {down}"
    ).format(total=client.traffic_used, up=client.traffic_up, down=client.traffic_down)

    return header_text + subscription_text + statistics_text


@router.callback_query(F.data == Navigation.PROFILE, IsPrivate())
async def callback_profile(callback: CallbackQuery, vpn_service: VPNService) -> None:
    """
    Handler for opening the user's profile.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        vpn_service (VPNService): Service for managing VPN subscriptions and data retrieval.
    """
    logger.info(f"User {callback.from_user.id} opened profile.")
    client_data = await vpn_service.get_client_data(callback.from_user.id)
    client = ClientService(client_data)

    if client:
        if not client.has_subscription_expired:
            reply_markup = show_key_keyboard()
        else:
            reply_markup = buy_subscription_keyboard()
    else:
        reply_markup = buy_subscription_keyboard()

    await callback.message.edit_text(
        text=await prepare_message(callback.from_user, client),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == Navigation.SHOW_KEY, IsPrivate())
async def callback_show_key(callback: CallbackQuery, vpn_service: VPNService) -> None:
    """
    Handler for showing the user's VPN key.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        vpn_service (VPNService): Service for managing VPN subscriptions and key retrieval.
    """
    logger.info(f"User {callback.from_user.id} looked key.")
    key = await vpn_service.get_key(callback.from_user.id)
    key_text = _("🔑 *Your key:* (Closes after {seconds_text}) ```{key}```")
    message = await callback.message.answer(key_text.format(key=key, seconds_text=_("6 seconds")))

    for seconds in range(5, 0, -1):
        seconds_text = _("1 second", "{} seconds", seconds).format(seconds)
        await asyncio.sleep(1)
        await message.edit_text(text=key_text.format(key=key, seconds_text=seconds_text))
    await message.delete()
