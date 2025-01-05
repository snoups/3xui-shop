import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.navigation import NavMain

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data.startswith(NavMain.CLOSE_NOTIFICATION), IsPrivate())
async def callback_close_notification(callback: CallbackQuery) -> None:
    """
    Handle the callback query to return to the main menu.

    Args:
        callback (CallbackQuery): The incoming callback query from the user.
    """
    logger.debug(f"User {callback.from_user.id} closed notification: {callback.message.message_id}")
    await callback.message.delete()
