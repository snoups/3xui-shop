import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.navigation import NavAdminTools

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.USER_EDITOR, IsAdmin())
async def callback_user_editor(callback: CallbackQuery) -> None:
    """
    Handler for opening the user editor.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    user: User = callback.from_user
    logger.info(f"Admin {user.id} opened user editor.")
    await callback.answer(text=_("Under development!"), show_alert=True)
