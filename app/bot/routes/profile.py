import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.i18n import gettext as _
from py3xui import AsyncApi, Client

from app.bot.filters import IsPrivate
from app.bot.keyboards.back import back_keyboard
from app.helpers import convert_size, parse_client_data, time_left_to_expiry

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def send_profile(
    user: User,
    api: AsyncApi,
    message: Message = None,
    callback: CallbackQuery = None,
) -> None:
    """
    Generates the user's profile information text based on their subscription and usage data.

    Args:
        user (User): The Telegram user object.

    Returns:
        str: The formatted profile information text.
    """
    client: Client = await api.client.get_by_email(user.id)
    client_data = parse_client_data(client)

    header_text = _("👤 Your Profile:\nName: {name}\nID: {id}").format(
        name=user.first_name,
        id=user.id,
    )

    if client_data:
        print(client_data)
        subscription_text = _("📅 Subscription:\nPlan: {plan}\n").format(
            plan=convert_size(client_data["plan"])
        )
        if client_data["remaining_traffic"] < -1:
            subscription_text += _("Traffic limit reached.")
        elif client_data["expiry_time"] < 0:
            subscription_text += _("Subscription period has expired.")
        else:
            subscription_text += _(
                "Remaining Traffic: {remaining_traffic}\nExpires on: {expiry_time}"
            ).format(
                remaining_traffic=convert_size(client_data["remaining_traffic"]),
                expiry_time=time_left_to_expiry(client_data["expiry_time"]),
            )
        statistics_text = _(
            "📊 Statistics:\nTotal Traffic: {total}\nSent: ↑ {up}\nReceived: ↓ {down}"
        ).format(
            total=convert_size(client_data["total"]),
            up=convert_size(client_data["up"]),
            down=convert_size(client_data["down"]),
        )
        text = f"{header_text}\n\n{subscription_text}\n\n{statistics_text}"
    else:
        no_subscription_text = _(
            "You haven't subscribed yet. Go to the subscription page to purchase one."
        )
        return f"{header_text}\n\n{no_subscription_text}"

    if callback:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=back_keyboard("main_menu"))
    elif message:
        await message.answer(text, reply_markup=back_keyboard("main_menu"))

    logger.debug(f"Sent profile to user {user.id}")


@router.message(Command("profile"), IsPrivate())
async def command_profile(message: Message, api: AsyncApi) -> None:
    """
    Handles the /profile command and sends the user's profile information.

    Args:
        message (Message): Incoming message from the user.
    """
    await send_profile(
        user=message.from_user,
        api=api,
        message=message,
    )


@router.callback_query(F.data == "profile", IsPrivate())
async def callback_profile(callback: CallbackQuery, api: AsyncApi) -> None:
    """
    Handles the callback query for the profile button, deletes the old message,
    and sends a new profile message.

    Args:
        callback (CallbackQuery): Callback query containing user interaction data.
    """
    await send_profile(
        user=callback.from_user,
        api=api,
        callback=callback,
    )
