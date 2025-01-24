import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavMain
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data.startswith(NavMain.CLOSE_NOTIFICATION))
async def callback_close_notification(callback: CallbackQuery, user: User) -> None:
    logger.debug(f"User {user.tg_id} closed notification: {callback.message.message_id}")
    try:
        await callback.message.delete()
        logger.debug(f"Notification for user {user.tg_id} deleted.")
    except Exception as exception:
        logger.error(f"Failed to delete notification for user {user.tg_id}: {exception}")
