import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot import commands, middlewares, routes
from app.config import Config, load_config
from app.db.database import Database
from app.logger import setup_logging

logger = logging.getLogger(__name__)


async def on_shutdown(dispatcher: Dispatcher, bot: Bot) -> None:
    """
    Shutdown event handler. This runs when the bot shuts down.
    """
    logger.info("Bot stopped")
    db: Database = dispatcher.get("db")
    config: Config = dispatcher.get("config")
    await bot.send_message(chat_id=config.bot.DEV_ID, text="#BotStopped")
    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()
    await db.close()


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    """
    Startup event handler. This runs when the bot starts up.
    """
    logger.info("Bot started")
    config: Config = dispatcher.get("config")
    await bot.send_message(chat_id=config.bot.DEV_ID, text="#BotStarted")


async def main() -> None:
    """
    Main function that initializes the bot and starts the event loop.
    """
    config = load_config()
    db = Database(config.database)
    storage = MemoryStorage()
    bot = Bot(
        token=config.bot.TOKEN,
    )
    dp = Dispatcher(
        storage=storage,
        config=config,
        bot=bot,
        db=db,
    )

    # Configure logging
    setup_logging(config.logging)

    # Register startup handler
    dp.startup.register(on_startup)
    # Register shutdown handler
    dp.shutdown.register(on_shutdown)
    # Register middlewares
    middlewares.register(dp, config=config, session=db.session)
    # Include routes
    routes.include(dp)

    # Initialize database
    await db.init()

    # Initialize commands
    await commands.setup(bot)

    # Start the bot
    await bot.delete_webhook()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
