import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.bot import commands, filters, middlewares, routes
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.services import NotificationService, VPNService, initialize
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
    db: Database = dispatcher.get("db")
    config: Config = dispatcher.get("config")
    notification_service: NotificationService = dispatcher.get("notification_service")

    if config.bot.DEV_ID:
        await notification_service.notify_by_id(config.bot.DEV_ID, "#BotStopped")

    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()
    await db.close()
    logger.info("Bot stopped.")


async def on_startup(dispatcher: Dispatcher, bot: Bot) -> None:
    """
    Handles bot startup events.

    Arguments:
        dispatcher (Dispatcher): The dispatcher instance.
        bot (Bot): The bot instance.
    """
    logger.info("Bot started.")
    config: Config = dispatcher.get("config")
    webhook_url = f"{config.bot.WEBHOOK}webhook"

    if await bot.get_webhook_info() != webhook_url:
        await bot.set_webhook(webhook_url)

    current_webhook = await bot.get_webhook_info()
    logger.info(f"Current webhook URL: {current_webhook.url}")

    notification_service: NotificationService = dispatcher.get("notification_service")

    if config.bot.DEV_ID:
        await notification_service.notify_by_id(config.bot.DEV_ID, "#BotStarted")


async def main() -> None:
    """
    Initializes the bot, sets up services, and runs the application.
    """
    # Create web application
    app = web.Application()

    # Load configuration
    config = load_config()

    # Set up logging
    setup_logging(config.logging)

    # Initialize database
    db = Database(config.database)

    # Set up in-memory storage for FSM (Finite State Machine)
    storage = MemoryStorage()  # TODO: RedisStorage

    # Initialize the bot with the token and default properties
    bot = Bot(
        token=config.bot.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN, link_preview_is_disabled=True),
    )

    # Initialize services
    services = initialize(app, config, db, bot)
    vpn_service: VPNService = services["vpn_service"]
    await vpn_service.initialize()

    # Set up internationalization (i18n)
    i18n = I18n(path=DEFAULT_LOCALES_DIR, default_locale="en", domain="bot")
    I18n.set_current(i18n)

    # Create the dispatcher with the storage, config, bot, database
    dispatcher = Dispatcher(storage=storage, config=config, bot=bot, **services)

    # Register event handlers
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    # Enable Maintenance mode for developing
    MaintenanceMiddleware.set_mode(True)

    # Register middlewares
    middlewares.register(dispatcher, i18n, db.session)

    # Register filters
    filters.register(dispatcher, config.bot.DEV_ID, config.bot.ADMINS)

    # Include bot routes
    routes.include(dispatcher)

    # Initialize database
    await db.initialize()

    # Set up bot commands
    await commands.setup(bot)

    # Set up webhook request handler
    webhook_requests_handler = SimpleRequestHandler(dispatcher, bot)
    webhook_requests_handler.register(app, path="/webhook")

    # Set up application and run
    setup_application(app, dispatcher, bot=bot)
    await web._run_app(app, host="0.0.0.0", port=config.bot.WEBHOOK_PORT)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
