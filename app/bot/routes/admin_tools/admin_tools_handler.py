import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsDev
from app.bot.navigation import NavAdminTools

from .keyboard import admin_tools_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAIN, IsAdmin())
async def callback_admin_tools(callback: CallbackQuery) -> None:
    """
    Handler for opening the admin tools menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    user: User = callback.from_user
    logger.info(f"Admin {user.id} opened admin tools.")
    is_dev = await IsDev()(callback)
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(is_dev),
    )
