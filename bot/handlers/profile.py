from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from utils.api import api, get_client_data, reset_traffic
from utils.localization import localization
from utils.logger import Logger

logger = Logger(__name__).get_logger()
router = Router(name="profile")


@router.message(Command("test"))
async def test(message: Message) -> None:
    user = message.from_user
    lang = user.language_code

    await reset_traffic(user.id)
    await message.answer("ok")


@router.message(Command("profile"))
async def command_profile(message: Message) -> None:
    """
    Handles the /profile command and sends the user's profile information.

    Args:
        message (Message): The incoming message from the user.
    """
    user = message.from_user
    lang = user.language_code

    client_data = await get_client_data(user.id, lang)

    header_text = localization.get_text("PROFILE_MESSAGE.HEADER", lang).format(
        user_name=user.first_name,
        user_id=user.id,
    )
    if client_data:
        subscription_text = localization.get_text("PROFILE_MESSAGE.SUBSCRIPTION", lang).format(
            plan=client_data["plan"],
            remaining_traffic=client_data["remaining_traffic"],
            expiry_time=client_data["expiry_time"],
        )
        statistics_text = localization.get_text("PROFILE_MESSAGE.STATISTICS", lang).format(
            total=client_data["total"],
            up=client_data["up"],
            down=client_data["down"],
        )
        text = f"{header_text}\n\n{subscription_text}\n\n{statistics_text}"
    else:
        no_subscription_text = localization.get_text("PROFILE_MESSAGE.NO_SUBSCRIPTION", lang)
        text = f"{header_text}\n\n{no_subscription_text}"

    logger.debug(f"Sent profile to user {user.id} with language {lang}")
    await message.answer(text)


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

    client_data = await get_client_data(user.id, lang)

    header_text = localization.get_text("PROFILE_MESSAGE.HEADER", lang).format(
        user_name=user.first_name,
        user_id=user.id,
    )
    if client_data:
        subscription_text = localization.get_text("PROFILE_MESSAGE.SUBSCRIPTION", lang).format(
            plan=client_data["plan"],
            remaining_traffic=client_data["remaining_traffic"],
            expiry_time=client_data["expiry_time"],
        )
        statistics_text = localization.get_text("PROFILE_MESSAGE.STATISTICS", lang).format(
            total=client_data["total"],
            up=client_data["up"],
            down=client_data["down"],
        )
        text = f"{header_text}\n\n{subscription_text}\n\n{statistics_text}"
    else:
        no_subscription_text = localization.get_text("PROFILE_MESSAGE.NO_SUBSCRIPTION", lang)
        text = f"{header_text}\n\n{no_subscription_text}"

    logger.debug(f"Handled callback for profile of user {user.id} with language {lang}")
    await callback.message.answer(text)


def register_handler(dp: Dispatcher) -> None:
    """
    Registers the router containing the profile command and callback handlers.

    Args:
        dp (Dispatcher): The dispatcher to which the router will be added.
    """
    dp.include_router(router)
    logger.debug("Profile handler registered.")
