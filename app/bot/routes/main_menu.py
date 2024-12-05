import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.main_menu import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(Command("start"), IsPrivate())
async def command_main_menu(message: Message) -> None:
    """
    Handles the /start command and sends the main menu message to the user.

    Args:
        message (Message): The incoming message from the user.
    """
    user = message.from_user

    text = _(
        """Welcome, {user_name}! 🎉

3X-UI SHOP — your reliable assistant in the world of free internet.
We offer safe and fast connections to any internet services using the XRAY protocol.
Our service works even in China, Iran, and Russia.
        
🚀 HIGH SPEED
🔒 SECURITY
📱 SUPPORT FOR ALL PLATFORMS
♾️ UNLIMITED
✅ GUARANTEE AND TRIAL PERIOD"""
    )

    text = text.format(user_name=user.full_name)

    logger.info(f"Sent main menu to user {user.id}")
    await message.answer(text, reply_markup=main_menu_keyboard())
