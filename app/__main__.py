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
from app.bot import filters, middlewares, routers, services, tasks
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.models import ServicesContainer
from app.bot.payment_gateways import GatewayFactory
from app.bot.utils import commands
from app.bot.utils.constants import (
    BOT_STARTED_TAG,
    BOT_STOPPED_TAG,
    DEFAULT_LANGUAGE,
    I18N_DOMAIN,
    TELEGRAM_WEBHOOK,
)
from app.config import DEFAULT_BOT_HOST, DEFAULT_LOCALES_DIR, Config, load_config
from app.db.database import Database


async def on_shutdown(db: Database, bot: Bot, services: ServicesContainer) -> None:
    await services.notification.notify_developer(BOT_STOPPED_TAG)
    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()
    await db.close()
    logging.info("Bot stopped.")


async def on_startup(config: Config, bot: Bot, services: ServicesContainer, db: Database) -> None:
    webhook_url = urljoin(config.bot.DOMAIN, TELEGRAM_WEBHOOK)

    if await bot.get_webhook_info() != webhook_url:
        await bot.set_webhook(webhook_url)

    current_webhook = await bot.get_webhook_info()
    logging.info(f"Current webhook URL: {current_webhook.url}")

    await services.notification.notify_developer(BOT_STARTED_TAG)
    logging.info("Bot started.")

    tasks.transactions.start_scheduler(db.session)
    if config.shop.REFERRER_REWARD_ENABLED:
        tasks.referral.start_scheduler(
            session_factory=db.session, referral_service=services.referral
        )


async def main() -> None:
    # Create web application
    app = Application()

    # Load configuration
    config = load_config()

    # Set up logging
    logger.setup_logging(config.logging)

    # Initialize database
    db = Database(config.database)
    await db.initialize()

    # Set up storage for FSM (Finite State Machine)
    storage = RedisStorage.from_url(url=config.redis.url())
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
    services_container = await services.initialize(config=config, session=db.session, bot=bot)

    # Sync servers
    await services_container.server_pool.sync_servers()

    # Register payment gateways
    gateway_factory = GatewayFactory()
    gateway_factory.register_gateways(
        app=app,
        config=config,
        session=db.session,
        storage=storage,
        bot=bot,
        i18n=i18n,
        services=services_container,
    )

    # Create the dispatcher
    dispatcher = Dispatcher(
        db=db,
        storage=storage,
        config=config,
        bot=bot,
        services=services_container,
        gateway_factory=gateway_factory,
    )

    # Register event handlers
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    # Enable Maintenance mode for developing # WARNING: remove before production
    MaintenanceMiddleware.set_mode(False)

    # Register middlewares
    middlewares.register(dispatcher=dispatcher, i18n=i18n, session=db.session)

    # Register filters
    filters.register(
        dispatcher=dispatcher,
        developer_id=config.bot.DEV_ID,
        admins_ids=config.bot.ADMINS,
    )

    # Include bot routers
    routers.include(app=app, dispatcher=dispatcher)

    # Set up bot commands
    await commands.setup(bot)

    # Set up webhook request handler
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dispatcher, bot=bot)
    webhook_requests_handler.register(app, path=TELEGRAM_WEBHOOK)

    # Set up application and run
    setup_application(app, dispatcher, bot=bot)
    await _run_app(app, host=DEFAULT_BOT_HOST, port=config.bot.PORT)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
