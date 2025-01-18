import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavMain

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data.startswith(NavMain.CLOSE_NOTIFICATION))
async def callback_close_notification(callback: CallbackQuery) -> None:
    user: User = callback.from_user
    logger.debug(f"User {user.id} closed notification: {callback.message.message_id}")
    try:
        await callback.message.delete()
        logger.debug(f"Notification for user {user.id} deleted.")
    except Exception as exception:
        logger.error(f"Failed to delete notification for user {user.id}: {exception}")
