import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.navigation import NavAdminTools
from app.bot.routes.admin_tools.keyboard import maintenance_mode_keyboard
from app.bot.services import NotificationService
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_MODE, IsAdmin())
async def callback_maintenance_mode(
    callback: CallbackQuery,
    user: User,
) -> None:
    logger.info(f"Admin {user.tg_id} navigated to maintenance mode options.")
    status = _("enabled.") if MaintenanceMiddleware.active else _("disabled.")
    await callback.message.edit_text(
        text=_("🚧 *Maintenance mode:*") + " " + status,
        reply_markup=maintenance_mode_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_ON, IsAdmin())
async def callback_maintenance_on(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} enabled maintenance mode.")
    MaintenanceMiddleware.set_mode(True)
    await callback.message.edit_text(
        text=_("🚧 *Maintenance mode:* enabled."),
        reply_markup=maintenance_mode_keyboard(),
    )
    await NotificationService.notify_by_message(
        message=callback.message,
        text=_("🟢 Maintenance mode enabled.\n" "_The bot is temporarily unavailable for users._"),
        duration=5,
    )


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_OFF, IsAdmin())
async def callback_maintenance_off(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} disabled maintenance mode.")
    MaintenanceMiddleware.set_mode(False)
    await callback.message.edit_text(
        text=_("🚧 *Maintenance mode:* disabled."),
        reply_markup=maintenance_mode_keyboard(),
    )
    await NotificationService.notify_by_message(
        message=callback.message,
        text=_("🔴 Maintenance mode disabled.\n" "_The bot is available for users._"),
        duration=5,
    )
