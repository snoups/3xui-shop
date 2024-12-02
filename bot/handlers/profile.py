from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User

import bot.utils.api as api
from bot.keyboards.back_keyboard import get_back_keyboard
from bot.utils.helpers import convert_size, time_left_to_expiry
from bot.utils.localization import localization
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
router = Router(name=__name__)


async def profile_handler(user: User) -> str:
    """
    Generates the user's profile information text based on their subscription and usage data.

    Args:
        user (User): The Telegram user object.

    Returns:
        str: The formatted profile information text.
    """
    lang = user.language_code
    client_data = await api.get_client_data(user.id)

    header_text = localization.get_text("PROFILE_MESSAGE.HEADER", lang).format(
        user_name=user.first_name,
        user_id=user.id,
    )

    if client_data:
        print(client_data)
        if client_data["remaining_traffic"] < -1:
            subscription_text = localization.get_text(
                "PROFILE_MESSAGE.SUBSCRIPTION_TRAFFIC_EXPIRED", lang
            ).format(plan=convert_size(client_data["plan"], lang))
        elif client_data["expiry_time"] < 0:
            subscription_text = localization.get_text(
                "PROFILE_MESSAGE.SUBSCRIPTION_TIME_EXPIRED", lang
            ).format(plan=convert_size(client_data["plan"], lang))
        else:
            subscription_text = localization.get_text("PROFILE_MESSAGE.SUBSCRIPTION", lang).format(
                plan=convert_size(client_data["plan"], lang),
                remaining_traffic=convert_size(client_data["remaining_traffic"], lang),
                expiry_time=time_left_to_expiry(client_data["expiry_time"], lang),
            )
        statistics_text = localization.get_text("PROFILE_MESSAGE.STATISTICS", lang).format(
            total=convert_size(client_data["total"], lang),
            up=convert_size(client_data["up"], lang),
            down=convert_size(client_data["down"], lang),
        )
        return f"{header_text}\n\n{subscription_text}\n\n{statistics_text}"
    else:
        no_subscription_text = localization.get_text("PROFILE_MESSAGE.SUBSCRIPTION_NONE", lang)
        return f"{header_text}\n\n{no_subscription_text}"


@router.message(Command("profile"))
async def command_profile(message: Message) -> None:
    """
    Handles the /profile command and sends the user's profile information.

    Args:
        message (Message): The incoming message from the user.
    """
    user = message.from_user
    lang = user.language_code
    text = await profile_handler(user)
    logger.debug(f"Sent profile to user {user.id}")
    await message.answer(text, reply_markup=get_back_keyboard(lang, "main_menu"))


@router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery) -> None:
    """
    Handles the callback query for the profile button, deletes the old message,
    and sends a new profile message.

    Args:
        callback (CallbackQuery): The callback query containing user interaction data.
    """
    user = callback.from_user
    lang = user.language_code
    await callback.message.delete()
    text = await profile_handler(user)
    logger.debug(f"Handled callback for profile of user {user.id}")
    await callback.message.answer(text, reply_markup=get_back_keyboard(lang, "main_menu"))


def register_handler(dp: Dispatcher) -> None:
    """
    Registers the router containing the profile command and callback handlers.

    Args:
        dp (Dispatcher): The dispatcher to which the router will be added.
    """
    dp.include_router(router)
    logger.debug("Profile handler registered.")
