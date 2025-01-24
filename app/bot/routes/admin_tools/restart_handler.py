import logging
import os
import sys

from aiogram import F, Router
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.navigation import NavAdminTools
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.RESTART_BOT, IsAdmin())
async def callback_restart_bot(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} restarted bot.")
    name = os.getenv("HOSTNAME", None)
    if name:
        os.system(f"docker restart {name}")  # TODO: Test docker
    else:
        os.execv(sys.executable, [sys.executable, *sys.argv])
