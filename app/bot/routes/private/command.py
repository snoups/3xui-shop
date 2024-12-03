import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.filters import IsPrivate

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"), IsPrivate())
async def handler(message: Message) -> None:
    """
    Example command.
    """
    await message.answer("Hello from Bot!")
    logger.info("Hello from Bot!")
