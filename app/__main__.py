import asyncio
import logging
from urllib.parse import urljoin

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import Application, _run_app

from app import logger
from app.bot import filters, middlewares, routers, services
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.models import ServicesContainer
from app.bot.utils import commands
from app.bot.utils.constants import (
    BOT_STARTED_TAG,
    BOT_STOPPED_TAG,
    DEFAULT_LANGUAGE,
    I18N_DOMAIN,
    TELEGRAM_WEBHOOK,
)
from app.config import DEFAULT_LOCALES_DIR, Config, load_config
from app.db.database import Database


async def on_shutdown(db: Database, bot: Bot, services: ServicesContainer) -> None:
    await services.notification.notify_developer(BOT_STOPPED_TAG)
    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()
    await db.close()
    logging.info("Bot stopped.")


async def on_startup(config: Config, bot: Bot, services: ServicesContainer) -> None:
    webhook_url = urljoin(config.bot.HOST, TELEGRAM_WEBHOOK)

    if await bot.get_webhook_info() != webhook_url:
        await bot.set_webhook(webhook_url)

    current_webhook = await bot.get_webhook_info()
    logging.info(f"Current webhook URL: {current_webhook.url}")

    await services.notification.notify_developer(BOT_STARTED_TAG)
    logging.info("Bot started.")


async def main() -> None:
    # Create web application
    app = Application()

    # Load configuration
    config = load_config()

    # Set up logging
    logger.setup_logging(config.logging)

    # Initialize database
    db = Database(config.database)

    # Set up storage for FSM (Finite State Machine)
    storage = RedisStorage.from_url("redis://0.0.0.0:6379/0")
    # storage = MemoryStorage()

    # Initialize the bot with the token and default properties
    bot = Bot(
        token=config.bot.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
    )

    # Set up internationalization (i18n)
    i18n = I18n(path=DEFAULT_LOCALES_DIR, default_locale=DEFAULT_LANGUAGE, domain=I18N_DOMAIN)
    I18n.set_current(i18n)

    # Initialize services
    services_container = await services.initialize(app, config, bot, db.session, storage)

    # Sync servers
    await services_container.server_pool.sync_servers()

    # Create the dispatcher with the storage, database, config, bot, services
    dispatcher = Dispatcher(
        storage=storage,
        db=db,
        config=config,
        bot=bot,
        services=services_container,
    )

    # Register event handlers
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    # Enable Maintenance mode for developing
    MaintenanceMiddleware.set_mode(True)

    # Register middlewares
    middlewares.register(dispatcher, i18n, db.session)

    # Register filters
    filters.register(dispatcher, config.bot.DEV_ID, config.bot.ADMINS)

    # Include bot routers
    routers.include(dispatcher, app)

    # Initialize database
    await db.initialize()

    # Set up bot commands
    await commands.setup(bot)

    # Set up webhook request handler
    webhook_requests_handler = SimpleRequestHandler(dispatcher, bot)
    webhook_requests_handler.register(app, path=TELEGRAM_WEBHOOK)

    # Set up application and run
    setup_application(app, dispatcher, bot=bot)
    await _run_app(app, host="0.0.0.0", port=config.bot.PORT)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
