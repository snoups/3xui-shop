import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.keyboards.main_menu import main_menu_keyboard
from app.bot.navigation import Navigation

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
        "3X-UI SHOP — your reliable assistant in the world of free internet. "
        "We offer safe and fast connections to any internet services using the XRAY protocol. "
        "Our service works even in China, Iran, and Russia.\n"
        "\n"
        "🚀 HIGH SPEED\n"
        "🔒 SECURITY\n"
        "📱 SUPPORT FOR ALL PLATFORMS\n"
        "♾️ UNLIMITED\n"
        "✅ GUARANTEE AND TRIAL PERIOD\n"
    ).format(name=user.full_name)


@router.message(Command(Navigation.START), IsPrivate())
async def command_main_menu(message: Message, state: FSMContext) -> None:
    """
    Handler for the `/start` command, displays the main menu to the user.

    Arguments:
        message (Message): The incoming message from the user.
        state (FSMContext): The FSM context to manage user state.
    """
    await message.delete()
    logger.info(f"User {message.from_user.id} opened main menu.")
    await state.clear()
    is_admin = await IsAdmin()(message)
    await message.answer(
        text=prepare_message(message.from_user),
        reply_markup=main_menu_keyboard(is_admin),
    )


@router.callback_query(F.data == Navigation.MAIN_MENU, IsPrivate())
async def callback_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for returning to the main menu via callback query.

    Arguments:
        callback (CallbackQuery): The incoming callback query from the user.
        state (FSMContext): The FSM context to manage user state.
    """
    logger.info(f"User {callback.from_user.id} returned to main menu.")
    await state.clear()
    is_admin = await IsAdmin()(callback)
    await callback.message.edit_text(
        text=prepare_message(callback.from_user),
        reply_markup=main_menu_keyboard(is_admin),
    )
