import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n

from app.bot import commands, filters, middlewares, routes
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.services import PlansService, PromocodeService, VPNService
from app.config import DEFAULT_LOCALES_DIR, Config, load_config
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
    logger.info("Bot stopped.")
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
    logger.info("Bot started.")
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

    # Setup logging
    setup_logging(config.logging)

    # Initialize components
    db = Database(config.database)
    storage = MemoryStorage()  # TODO: REDIS
    bot = Bot(token=config.bot.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher(storage=storage, config=config, bot=bot, db=db)
    i18n = I18n(path=DEFAULT_LOCALES_DIR, default_locale="en", domain="bot")
    plans_service = PlansService()
    promocode_service = PromocodeService(db.session)
    vpn_service = VPNService(db.session, config, promocode_service)

    # Register event handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Register developer in IsDev filter
    filters.register_developer(config.bot.DEV_ID)

    # Register admins in IsAdmin filter
    filters.register_admins(config.bot.ADMINS)

    # Enable Maintenance mode for developing
    MaintenanceMiddleware.set_mode(True)

    # Register middlewares
    middlewares.register(
        bot,
        dp,
        config=config,
        session=db.session,
        i18n=i18n,
        plans=plans_service,
        promocode=promocode_service,
        vpn=vpn_service,
    )

    # Include bot routes
    routes.include(dp)

    # Initialize database
    await db.initialize()

    # Initialize VPNService
    await vpn_service.initialize()

    # Set up bot commands
    await commands.setup(bot)

    # Start bot polling
    await bot.delete_webhook()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
