from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.bot.navigation import NavigationAction


async def setup(bot: Bot) -> None:
    """
    Configure bot commands for private chats.

    Arguments:
        bot (Bot): The bot instance to configure commands for.
    """
    commands = [
        BotCommand(command=NavigationAction.START, description="Открыть главное меню"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )


async def delete(bot: Bot) -> None:
    """
    Remove bot commands from private chats.

    Arguments:
        bot (Bot): The bot instance to remove commands from.
    """
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats(),
    )
