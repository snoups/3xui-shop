import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.back import back_keyboard
from app.bot.keyboards.profile import buy_subscription_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services.client import ClientService
from app.bot.services.vpn import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def prepare_message(user: User, client: ClientService) -> str:
    """
    Prepares the user's profile message, including subscription and statistics details.

    Arguments:
        user (User): The user for whom the profile message is being prepared.
        client (ClientService): The client service to retrieve subscription and statistics.

    Returns:
        str: A formatted message with the user's profile, subscription, and statistics.
    """
    header_text = _("👤 Your Profile:\n" "Name: {name}\n" "ID: {id}\n\n").format(
        name=user.first_name,
        id=user.id,
    )

    if not client:
        no_subscription_text = _(
            "You don't have a subscription purchased yet, go to the subscription page "
            "to purchase or click the button below."
        )
        return header_text + no_subscription_text

    subscription_text = _("📅 Subscription:\nPlan: {plan}\n").format(plan=client.traffic_total)

    if client.has_traffic_expired:
        subscription_text += _("Traffic limit reached.\n")
        if not client.has_subscription_expired:
            subscription_text += _("Expires on: {expiry_time}\n").format(
                expiry_time=client.expiry_time,
            )
    if client.has_subscription_expired:
        if not client.has_traffic_expired:
            subscription_text += _("Remaining Traffic: {traffic}\n").format(
                traffic=client.traffic_remaining,
            )
        subscription_text += _("Subscription period has expired.\n")

    if client.has_valid_subscription:
        subscription_text += _(
            "Remaining Traffic: {traffic}\nExpires on: {expiry_time}\n\n"
        ).format(
            traffic=client.traffic_remaining,
            expiry_time=client.expiry_time,
        )
    else:
        subscription_text += "\n"

    statistics_text = _(
        "📊 Statistics:\nTotal Traffic: {total}\nSent: ↑ {up}\nReceived: ↓ {down}"
    ).format(total=client.traffic_used, up=client.traffic_up, down=client.traffic_down)

    # TODO: add subscription key view

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
    await callback.message.delete()

    data = await vpn.get_client_data(callback.from_user.id)
    client = ClientService(data)

    if client:
        if client.has_valid_subscription:
            reply_markup = back_keyboard(NavigationAction.MAIN_MENU)
        else:
            reply_markup = buy_subscription_keyboard()
    else:
        reply_markup = buy_subscription_keyboard()

    await callback.message.answer(
        await prepare_message(callback.from_user, client),
        reply_markup=reply_markup,
    )
