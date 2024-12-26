import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsMaintenanceMode, IsPrivate
from app.bot.navigation import Navigation

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.message(IsMaintenanceMode(), Command(Navigation.START), IsPrivate(), ~IsAdmin())
async def command_start(message: Message):
    """
    Handles messages in private chats from non-admin users.

    Arguments:
        message (Message): The incoming message from the user.
    """
    logger.info(f"User {message.from_user.id} tried to message the bot during maintenance.")
    await message.answer(_("The bot is in maintenance mode. Please wait."))


@router.callback_query(IsMaintenanceMode(), IsPrivate(), ~IsAdmin())
async def callback_any(callback: CallbackQuery):
    """
    Handles callback queries in private chats from non-admin users.

    Arguments:
        callback (CallbackQuery): The incoming callback query from the user.
    """
    logger.info(f"User {callback.from_user.id} tried to interact with the bot during maintenance.")
    await callback.answer(text=_("The bot is in maintenance mode. Please wait."), show_alert=True)
