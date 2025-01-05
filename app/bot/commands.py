from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from app.bot.navigation import NavMain


async def setup(bot: Bot) -> None:
    """
    Configures bot commands for all private chats.

    This function sets the bot commands that will be available to all users
    in private chats. These commands are visible to the user and can be
    triggered by entering the command in the chat.

    Arguments:
        bot (Bot): The bot instance that will be configured with commands.
    """
    commands = [
        BotCommand(command=NavMain.START, description="Открыть главное меню"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )


async def delete(bot: Bot) -> None:
    """
    Removes all bot commands from private chats.

    This function deletes all the previously set commands from the bot, making
    them unavailable to the users in private chats. This is useful when you
    want to clear the command list or when the bot is being updated.

    Arguments:
        bot (Bot): The bot instance to remove commands from.
    """
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats(),
    )
