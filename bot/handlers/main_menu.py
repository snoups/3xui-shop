from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.utils.localization import localization
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
router = Router(name="main_menu")


@router.message(Command("start"))
async def command_main_menu(message: Message) -> None:
    """
    Handles the /start command and sends the main menu message to the user.

    Args:
        message (Message): The incoming message from the user.
    """
    user = message.from_user
    lang = message.from_user.language_code
    text = localization.get_text("MAIN_MENU_MESSAGE", lang).format(user_name=user.full_name)
    logger.debug(f"Sent main menu to user {message.from_user.id} with language {lang}")
    await message.answer(text, reply_markup=get_main_menu_keyboard(lang))


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    """
    Handles the callback query for the main menu button, deletes the old message, and
    sends a new main menu message.

    Args:
        callback (CallbackQuery): The callback query containing user interaction data.
    """
    user = callback.from_user
    lang = callback.from_user.language_code
    await callback.message.delete()
    text = localization.get_text("MAIN_MENU_MESSAGE", lang).format(user_name=user.full_name)
    logger.debug(f"Handled callback for user {callback.from_user.id} with language {lang}")
    await callback.message.answer(text, reply_markup=get_main_menu_keyboard(lang))


def register_handler(dp: Dispatcher) -> None:
    """
    Registers the router containing the main menu command and callback handlers.

    Args:
        dp (Dispatcher): The dispatcher to which the router will be added.
    """
    dp.include_router(router)
    logger.debug("Main menu handler registered.")
