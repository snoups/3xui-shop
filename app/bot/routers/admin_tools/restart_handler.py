import logging
import os
import sys

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.navigation import NavAdminTools
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.RESTART_BOT, IsAdmin())
async def callback_restart_bot(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} restarted bot.")

    await services.notification.show_popup(
        callback=callback,
        text=_("restart_bot:popup:process"),
    )

    os.execv(sys.executable, [sys.executable, *sys.argv])
