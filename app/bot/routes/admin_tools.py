import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.keyboards.admin_tools import admin_tools_keyboard
from app.bot.navigation import NavigationAction

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavigationAction.ADMIN_TOOLS, IsPrivate(), IsAdmin())
async def callback_statistics(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened admin tools.")
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(),
    )


@router.callback_query(F.data == NavigationAction.STATISTICS, IsPrivate(), IsAdmin())
async def callback_statistics(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened statistics.")
    pass


@router.callback_query(F.data == NavigationAction.EDITOR_USER, IsPrivate(), IsAdmin())
async def callback_editor_user(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened editor user.")
    pass


@router.callback_query(F.data == NavigationAction.SEND_NOTIFICATION, IsPrivate(), IsAdmin())
async def callback_send_notification(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened send notification.")
    pass


@router.callback_query(F.data == NavigationAction.CREATE_BACKUP, IsPrivate(), IsAdmin())
async def callback_create_backup(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} created backup.")
    pass


@router.callback_query(F.data == NavigationAction.RESTART_BOT, IsPrivate(), IsAdmin())
async def callback_restart_bot(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} restarted bot.")
    pass
