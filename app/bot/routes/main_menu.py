import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.main_menu import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def send_main_menu(
    user: User,
    message: Message = None,
    callback: CallbackQuery = None,
) -> None:
    """
    Sends the main menu message with keyboard.

    Args:
        user (User): The user object.
        message (Message): Optional. The message object for direct response.
        callback (CallbackQuery): Optional. The callback object for response.
    """
    text = _(
        """Welcome, {name}! 🎉

3X-UI SHOP — your reliable assistant in the world of free internet.
We offer safe and fast connections to any internet services using the XRAY protocol.
Our service works even in China, Iran, and Russia.

🚀 HIGH SPEED
🔒 SECURITY
📱 SUPPORT FOR ALL PLATFORMS
♾️ UNLIMITED
✅ GUARANTEE AND TRIAL PERIOD"""
    ).format(name=user.full_name)

    if callback:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=main_menu_keyboard())
    elif message:
        await message.answer(text, reply_markup=main_menu_keyboard())

    logger.info(f"Sent main menu to user {user.id}")


@router.message(Command("start"), IsPrivate())
async def command_main_menu(message: Message) -> None:
    """
    Handles the /start command and sends the main menu message to the user.

    Args:
        message (Message): Incoming message from the user.
    """
    await send_main_menu(
        user=message.from_user,
        message=message,
    )


@router.callback_query(F.data == "main_menu", IsPrivate())
async def callback_main_menu(callback: CallbackQuery) -> None:
    """
    Handles the callback query for the main menu button, deletes the old message, and
    sends a new main menu message.

    Args:
        callback (CallbackQuery): Callback query containing user interaction data.
    """
    await send_main_menu(
        user=callback.from_user,
        callback=callback,
    )
