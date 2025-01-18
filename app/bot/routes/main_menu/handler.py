import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.navigation import NavMain

from .keyboard import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


def prepare_message(user: User) -> str:
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


@router.message(Command(NavMain.START))
async def command_main_menu(message: Message, state: FSMContext) -> None:
    user: User = message.from_user
    logger.info(f"User {user.id} opened main menu page.")
    previous_message_id = await state.get_value("message_id")

    if previous_message_id:
        try:
            await message.bot.delete_message(chat_id=user.id, message_id=previous_message_id)
            logger.debug(f"Main message for user {user.id} deleted.")
        except Exception as exception:
            logger.error(f"Failed to delete main message for user {user.id}: {exception}")
        await state.clear()

    is_admin = await IsAdmin()(message)
    main_menu_message = await message.answer(
        text=prepare_message(user),
        reply_markup=main_menu_keyboard(is_admin),
    )
    await state.update_data(message_id=main_menu_message.message_id)
    await message.delete()


@router.callback_query(F.data == NavMain.MAIN_MENU)
async def callback_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} returned to main menu page.")
    await state.clear()
    await state.update_data(message_id=callback.message.message_id)
    is_admin = await IsAdmin()(callback)
    await callback.message.edit_text(
        text=prepare_message(user),
        reply_markup=main_menu_keyboard(is_admin),
    )
