import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"), IsPrivate())
async def handler(message: Message) -> None:
    """
    Example command.
    """
    await message.answer(_("Hello from Bot!"))
