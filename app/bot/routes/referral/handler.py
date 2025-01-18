import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavRefferal

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavRefferal.MAIN)
async def callback_referral(callback: CallbackQuery) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} opened referral page.")
    await callback.answer(text=_("Under development!"), show_alert=True)
