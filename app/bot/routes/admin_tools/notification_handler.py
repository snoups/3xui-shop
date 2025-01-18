import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.navigation import NavAdminTools

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.SEND_NOTIFICATION, IsAdmin())
async def callback_send_notification(callback: CallbackQuery) -> None:
    """
    Handler for sending notifications.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened send notification.")
    await callback.answer(text=_("Under development!"), show_alert=True)
