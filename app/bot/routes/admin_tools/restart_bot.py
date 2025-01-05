import logging
import os
import sys

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.navigation import NavAdminTools

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.RESTART_BOT, IsPrivate(), IsAdmin())
async def callback_restart_bot(callback: CallbackQuery, dispatcher: Dispatcher) -> None:
    """
    Handler for restarting the bot.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} restarted bot.")
    await dispatcher.stop_polling()
    name = os.getenv("HOSTNAME", None)
    if name:
        os.system(f"docker restart {name}")  # TODO: Test docker
    else:
        os.execv(sys.executable, [sys.executable, *sys.argv])
