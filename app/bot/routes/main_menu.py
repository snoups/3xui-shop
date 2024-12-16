import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.navigation import NavigationAction

logger = logging.getLogger(__name__)
router = Router(name=__name__)


def prepare_message(user: User) -> str:
    """
    Prepares a welcome message for the user.

    Arguments:
        user (User): The user for whom the welcome message is being prepared.

    Returns:
        str: A formatted welcome message with user name.
    """
    return _(
        "Welcome, {name}! 🎉\n"
        "\n"
        "3X-UI SHOP — your reliable assistant in the world of free internet.\n"
        "We offer safe and fast connections to any internet services using the XRAY protocol.\n"
        "Our service works even in China, Iran, and Russia.\n"
        "\n"
        "🚀 HIGH SPEED\n"
        "🔒 SECURITY\n"
        "📱 SUPPORT FOR ALL PLATFORMS\n"
        "♾️ UNLIMITED\n"
        "✅ GUARANTEE AND TRIAL PERIOD\n"
    ).format(name=user.full_name)


@router.message(Command(NavigationAction.START), IsPrivate())
async def command_main_menu(message: Message) -> None:
    """
    Handles the `/start` command and sends the main menu to the user.

    Arguments:
        message (Message): The incoming message with the `/start` command.
    """
    await message.answer(
        text=prepare_message(message.from_user),
        reply_markup=main_menu_keyboard(),
    )
    logger.info(f"User {message.from_user.id} opened main menu.")


@router.callback_query(F.data == NavigationAction.MAIN_MENU, IsPrivate())
async def callback_main_menu(callback: CallbackQuery) -> None:
    """
    Handles the callback query to return to the main menu and sends the updated message to the user.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
    """
    await callback.message.delete()
    await callback.message.answer(
        text=prepare_message(callback.from_user),
        reply_markup=main_menu_keyboard(),
    )
    logger.info(f"User {callback.from_user.id} returned to main menu.")
