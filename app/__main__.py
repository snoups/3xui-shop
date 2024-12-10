import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from py3xui import AsyncApi

from app.bot import commands, middlewares, routes
from app.config import Config, load_config
from app.db.database import Database
from app.logger import setup_logging

logger = logging.getLogger(__name__)


async def on_shutdown(dispatcher: Dispatcher, bot: Bot) -> None:
    """
    Handles bot shutdown events.

    Arguments:
        dispatcher (Dispatcher): The dispatcher instance.
        bot (Bot): The bot instance.
    """
    logger.info("Bot stopped")
    db: Database = dispatcher.get("db")
    config: Config = dispatcher.get("config")

    # Notify developer about bot stop
    if config.bot.DEV_ID:
        await bot.send_message(chat_id=config.bot.DEV_ID, text="#BotStopped")

    # Cleanup resources
    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()
    await db.close()


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    """
    Handles bot startup events.

    Arguments:
        dispatcher (Dispatcher): The dispatcher instance.
        bot (Bot): The bot instance.
    """
    logger.info("Bot started")
    config: Config = dispatcher.get("config")

    # Notify developer about bot start
    if config.bot.DEV_ID:
        await bot.send_message(chat_id=config.bot.DEV_ID, text="#BotStarted")


async def main() -> None:
    """
    Main function that initializes the bot and starts polling.
    """
    # Load configuration
    config = load_config()

    # Initialize components
    db = Database(config.database)
    storage = MemoryStorage()  # TODO: REDIS
    bot = Bot(token=config.bot.TOKEN)
    dp = Dispatcher(storage=storage, config=config, bot=bot, db=db)

    # Configure i18n
    i18n = I18n(path="app/locales", default_locale="en", domain="bot")

    # Initialize XUI API
    api = AsyncApi(
        host=config.xui.HOST,
        username=config.xui.USERNAME,
        password=config.xui.PASSWORD,
        token=config.xui.TOKEN,
        use_tls_verify=False,
        logger=logging.getLogger("xui"),
    )

    # Setup logging
    setup_logging(config.logging)

    # Register event handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Register middlewares
    middlewares.register(dp, config=config, session=db.session, api=api, i18n=i18n)

    # Include bot routes
    routes.include(dp)

    # Initialize database
    await db.init()

    # Set up bot commands
    await commands.setup(bot)

    # Authenticate for the XUI API
    await api.login()

    # Start bot polling
    await bot.delete_webhook()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
