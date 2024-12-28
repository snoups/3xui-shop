from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import SimpleI18nMiddleware

from .config import ConfigMiddleware
from .database import DBSessionMiddleware
from .maintenance import MaintenanceMiddleware
from .services import ServicesMiddleware
from .throttling import ThrottlingMiddleware


def register(bot: Bot, dp: Dispatcher, **kwargs) -> None:
    """
    Register middlewares to extend the bot's functionality.

    This function sets up the following middlewares:
    - ConfigMiddleware: Injects configuration settings.
    - DBSessionMiddleware: Provides a database session.
    - SimpleI18nMiddleware: Adds internationalization support.
    - MaintenanceMiddleware: Handles maintenance mode logic.
    - ServicesMiddleware: Supplies services like VPN, plans, and promocodes.
    - ThrottlingMiddleware: Implements rate limiting.

    Arguments:
        dp (Dispatcher): Dispatcher instance to register middlewares on.
        kwargs (Any): Middleware dependencies such as config, session, services, and throttling.
    """
    dp.update.outer_middleware.register(ThrottlingMiddleware())
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(SimpleI18nMiddleware(kwargs["i18n"]))
    dp.update.outer_middleware.register(MaintenanceMiddleware(bot))
    dp.update.outer_middleware.register(
        ServicesMiddleware(
            vpn_service=kwargs["vpn"],
            plans_service=kwargs["plans"],
            promocode_service=kwargs["promocode"],
        )
    )


__all__ = [
    "register",
]
