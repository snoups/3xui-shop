from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def setup(bot: Bot) -> None:
    """
    Configure bot commands for private chats.

    Args:
        bot (Bot): The bot instance to configure commands for.
    """
    commands = [
        BotCommand(command="start", description="Restart bot"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )


async def delete(bot: Bot) -> None:
    """
    Remove bot commands from private chats.

    Args:
        bot (Bot): The bot instance to remove commands from.
    """
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats(),
    )
