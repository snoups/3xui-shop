import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.navigation import NavRefferal

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavRefferal.MAIN, IsPrivate())
async def callback_referral(callback: CallbackQuery) -> None:
    """
    Handler for opening the referral page.

    Args:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"User {callback.from_user.id} opened referral page.")
    await callback.answer(text=_("Under development!"), show_alert=True)
