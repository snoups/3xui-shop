import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types import User as TelegramUser
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.profile import buy_subscription_keyboard, show_key_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services.client import ClientService
from app.bot.services.vpn import VPNService

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
    header_text = (
        _("👤 *Your profile:*\n" "Name: {name}\n" "ID: {id}\n").format(
            name=user.first_name, id=user.id
        )
        + "\n"
    )

    if not client:
        no_subscription_text = _(
            "_You don't have a subscription purchased yet, go to the subscription page "
            "to purchase or click the button below._"
        )
        return header_text + no_subscription_text

    subscription_text = _("📅 *Subscription:*\n" "Plan: {plan}\n").format(plan=client.traffic_total)

    if client.has_traffic_expired:
        subscription_text += _("_Traffic limit reached._\n")
        if not client.has_subscription_expired:
            subscription_text += _("Expires on: {expiry_time}\n").format(
                expiry_time=client.expiry_time,
            )
    if client.has_subscription_expired:
        if not client.has_traffic_expired:
            subscription_text += _("Remaining Traffic: {traffic}\n").format(
                traffic=client.traffic_remaining,
            )
        subscription_text += _("_Subscription period has expired._\n")

    if client.has_valid_subscription:
        subscription_text += (
            _("Remaining Traffic: {traffic}\n" "Expires on: {expiry_time}\n").format(
                traffic=client.traffic_remaining,
                expiry_time=client.expiry_time,
            )
            + "\n"
        )
    else:
        subscription_text += "\n"

    statistics_text = _(
        "📊 *Statistics:*\n" "Total: {total}\n" "Sent: ↑ {up}\n" "Received: ↓ {down}"
    ).format(total=client.traffic_used, up=client.traffic_up, down=client.traffic_down)

    return header_text + subscription_text + statistics_text


@router.callback_query(F.data == NavigationAction.PROFILE, IsPrivate())
async def callback_profile(callback: CallbackQuery, vpn: VPNService) -> None:
    """
    Handles the user's profile view, displaying subscription status and statistics.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        vpn (VPNService): The VPN service instance.
    """
    logger.info(f"User {callback.from_user.id} opened profile.")
    data = await vpn.get_client_data(callback.from_user.id)
    client = ClientService(data)

    if client:
        if client.has_valid_subscription:
            reply_markup = show_key_keyboard()
        else:
            reply_markup = buy_subscription_keyboard()
    else:
        reply_markup = buy_subscription_keyboard()

    await callback.message.edit_text(
        await prepare_message(callback.from_user, client),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == NavigationAction.SHOW_KEY, IsPrivate())
async def callback_show_key(callback: CallbackQuery, vpn: VPNService) -> None:
    """
    Sends the user's VPN key and deletes it after a short time.

    This handler is triggered when the user requests to view their VPN key. The key
    is sent to the user and automatically deleted after 5 seconds.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        vpn (VPNService): The VPN service instance.
    """
    key = await vpn.get_key(callback.from_user.id)

    key_text = _("🔑 *Your key:* (Closes after {seconds_text}) ```{key}```")
    message = await callback.message.answer(key_text.format(key=key, seconds_text=_("6 seconds")))
    for seconds in range(5, 0, -1):
        seconds_text = _("1 second", "{} seconds", seconds).format(seconds)
        await asyncio.sleep(1)
        await message.edit_text(key_text.format(key=key, seconds_text=seconds_text))
    await message.delete()
