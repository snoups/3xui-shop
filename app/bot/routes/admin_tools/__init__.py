import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsDev, IsPrivate
from app.bot.keyboards.admin_tools import admin_tools_keyboard
from app.bot.navigation import NavAdminTools

from . import (
    create_backup,
    maintenance_mode,
    promocode_editor,
    restart_bot,
    send_notification,
    server_management,
    statistics,
    user_editor,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)

router.include_router(server_management.router)
router.include_router(statistics.router)
router.include_router(user_editor.router)
router.include_router(promocode_editor.router)
router.include_router(send_notification.router)
router.include_router(create_backup.router)
router.include_router(maintenance_mode.router)
router.include_router(restart_bot.router)


@router.callback_query(F.data == NavAdminTools.MAIN, IsPrivate(), IsAdmin())
async def callback_admin_tools(callback: CallbackQuery) -> None:
    """
    Handler for opening the admin tools menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened admin tools.")
    is_dev = await IsDev()(callback)
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(is_dev),
    )
