from aiogram import Bot
from aiohttp.web import Application

from app.config import Config
from app.db.database import Database

from .client import ClientData
from .notification import NotificationService
from .payment import PaymentService
from .plan import PlanService
from .promocode import PromocodeService
from .server import ServerService
from .vpn import VPNService


def initialize(app: Application, config: Config, db: Database, bot: Bot) -> dict:
    """
    Initializes and registers various services for the bot.

    Arguments:
        app (Application): The Aiohttp application instance used to configure routes.
        config (Config): The configuration object containing settings for the services.
        db (Database): The database instance used for interacting with the database.
        bot (Bot): The Telegram bot instance used for interacting with users.

    Returns:
        dict: A dictionary containing the initialized services for the bot.
    """
    notification_service = NotificationService(bot)
    plan_service = PlanService()
    promocode_service = PromocodeService(db.session)
    server_service = ServerService(db.session)
    vpn_service = VPNService(db.session, config, promocode_service)
    payment_service = PaymentService(app, config, bot, db.session, vpn_service)

    return {
        "notification_service": notification_service,
        "plan_service": plan_service,
        "promocode_service": promocode_service,
        "server_service": server_service,
        "vpn_service": vpn_service,
        "payment_service": payment_service,
    }
