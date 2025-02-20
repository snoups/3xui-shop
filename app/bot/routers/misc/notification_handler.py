import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.routers.download.handler import callback_download
from app.bot.utils.navigation import NavMain
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


@router.callback_query(F.data.startswith(NavMain.REDIRECT_TO_DOWNLOAD))
async def callback_redirect_to_download(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    logger.debug(f"User {user.tg_id} redirected to download: {callback.message.message_id}")
    try:
        await callback.message.delete()
        logger.debug(f"Notification for user {user.tg_id} deleted.")
    except Exception as exception:
        logger.error(f"Failed to delete notification for user {user.tg_id}: {exception}")

    await callback_download(callback=callback, user=user, state=state)
