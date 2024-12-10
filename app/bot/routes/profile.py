import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _
from py3xui import AsyncApi

from app.bot.filters import IsPrivate
from app.bot.keyboards.back import back_keyboard
from app.bot.keyboards.profile import profile_keyboard
from app.bot.navigation import NavigationAction
from app.bot.services.profile import ProfileService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def prepare_message(user: User, profile_service: ProfileService) -> str:
    """
    Prepares a profile message for the user, including subscription and statistics details.

    Arguments:
        user (User): The user for whom the profile message is being prepared.
        api (AsyncApi): The API instance to retrieve client data.

    Returns:
        str: A formatted message containing the user's profile, subscription, and statistics.
    """
    header_text = _("👤 Your Profile:\n" "Name: {name}\n" "ID: {id}\n\n").format(
        name=user.first_name,
        id=user.id,
    )

    if not profile_service.has_valid_data():
        no_subscription_text = _(
            "You don't have a subscription purchased yet, go to the subscription page "
            "to purchase or click the button below."
        )
        return header_text + no_subscription_text

    subscription_text = _("📅 Subscription:\nPlan: {plan}\n").format(plan=profile_service.plan)

    if profile_service.has_traffic_expired():
        subscription_text += _("Traffic limit reached.\n")
    if profile_service.has_subscription_expired():
        subscription_text += _("Subscription period has expired.\n")
    if not profile_service.has_traffic_expired() and not profile_service.has_subscription_expired():
        subscription_text += _(
            "Remaining Traffic: {remaining_traffic}\nExpires on: {expiry_time}\n\n"
        ).format(
            remaining_traffic=profile_service.remaining_traffic,
            expiry_time=profile_service.expiry_time,
        )
    else:
        subscription_text += "\n"

    statistics_text = _(
        "📊 Statistics:\nTotal Traffic: {total}\nSent: ↑ {up}\nReceived: ↓ {down}"
    ).format(total=profile_service.total, up=profile_service.up, down=profile_service.down)

    return header_text + subscription_text + statistics_text


@router.callback_query(F.data == NavigationAction.PROFILE, IsPrivate())
async def callback_profile(callback: CallbackQuery, api: AsyncApi) -> None:
    """
    Handles the callback query to display the user's profile with subscription and statistics.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
        api (AsyncApi): The API instance to retrieve client data.
    """
    await callback.message.delete()

    client = await api.client.get_by_email(callback.from_user.id)
    profile_service = ProfileService(client)

    if profile_service.has_valid_data():
        reply_markup = back_keyboard(NavigationAction.MAIN_MENU)
    else:
        reply_markup = profile_keyboard()

    await callback.message.answer(
        await prepare_message(callback.from_user, profile_service),
        reply_markup=reply_markup,
    )
    logger.info(f"User {callback.from_user.id} open profile.")
