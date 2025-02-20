import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.utils.navigation import NavAdminTools
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.USER_EDITOR, IsAdmin())
async def callback_user_editor(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} opened user editor.")
    await callback.answer(text=_("global:popup:development"), show_alert=True)
