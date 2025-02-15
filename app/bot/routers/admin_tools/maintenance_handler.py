import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.navigation import NavAdminTools
from app.db.models import User

from .keyboard import maintenance_mode_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_MODE, IsAdmin())
async def callback_maintenance_mode(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} navigated to maintenance mode options.")
    from app.bot.middlewares import MaintenanceMiddleware

    status = (
        _("maintenance:status:enabled")
        if MaintenanceMiddleware.active
        else _("maintenance:status:disabled")
    )
    await callback.message.edit_text(
        text=_("maintenance:message:main").format(status=status),
        reply_markup=maintenance_mode_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_MODE_ENABLE, IsAdmin())
async def callback_maintenance_mode_enable(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} enabled maintenance mode.")
    from app.bot.middlewares import MaintenanceMiddleware

    MaintenanceMiddleware.set_mode(True)
    await callback.message.edit_text(
        text=_("maintenance:message:main").format(status=_("maintenance:status:enabled")),
        reply_markup=maintenance_mode_keyboard(),
    )
    await services.notification.show_popup(
        callback=callback,
        text=_("maintenance:popup:enabled"),
    )


@router.callback_query(F.data == NavAdminTools.MAINTENANCE_MODE_DISABLE, IsAdmin())
async def callback_maintenance_mode_disable(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} disabled maintenance mode.")
    from app.bot.middlewares import MaintenanceMiddleware

    MaintenanceMiddleware.set_mode(False)
    await callback.message.edit_text(
        text=_("maintenance:message:main").format(status=_("maintenance:status:disabled")),
        reply_markup=maintenance_mode_keyboard(),
    )
    await services.notification.show_popup(
        callback=callback,
        text=_("maintenance:popup:disabled"),
    )
