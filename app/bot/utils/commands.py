import logging

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from .navigation import NavMain

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    commands = [
        BotCommand(command=NavMain.START, description="Открыть главное меню"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )
    logger.info("Bot commands configured successfully.")


async def delete(bot: Bot) -> None:
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats(),
    )
    logger.info("Bot commands removed successfully.")
