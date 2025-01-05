import asyncio
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.keyboards.admin_tools import maintenance_mode_keyboard
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.navigation import NavAdminTools
from app.bot.services import NotificationService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_MODE, IsPrivate(), IsAdmin())
async def callback_maintenance_mode(callback: CallbackQuery) -> None:
    """
    Handler to display the option for enabling or disabling maintenance mode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} navigated to maintenance mode options.")
    status = _("enabled.") if MaintenanceMiddleware.active else _("disabled.")
    await callback.message.edit_text(
        text=_("🚧 *Maintenance mode:*") + " " + status,
        reply_markup=maintenance_mode_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_ON, IsPrivate(), IsAdmin())
async def callback_maintenance_on(callback: CallbackQuery) -> None:
    """
    Handler to enable the maintenance mode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} enabled maintenance mode.")
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


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_OFF, IsPrivate(), IsAdmin())
async def callback_maintenance_off(callback: CallbackQuery) -> None:
    """
    Handler to disable the maintenance mode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} disabled maintenance mode.")
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
