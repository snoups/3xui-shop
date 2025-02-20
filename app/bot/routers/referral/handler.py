import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.utils.navigation import NavReferral
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavReferral.MAIN)
async def callback_referral(callback: CallbackQuery, user: User) -> None:
    logger.info(f"User {user.tg_id} opened referral page.")
    await callback.answer(text=_("global:popup:development"), show_alert=True)
