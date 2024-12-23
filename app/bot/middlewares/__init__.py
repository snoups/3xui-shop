from aiogram import Dispatcher
from aiogram.utils.i18n import SimpleI18nMiddleware

from .config import ConfigMiddleware
from .database import DBSessionMiddleware
from .services import ServicesMiddleware
from .throttling import ThrottlingMiddleware


def register(dp: Dispatcher, **kwargs) -> None:
    """
    Registers multiple middlewares for the bot to handle various tasks such as
    configuration, database session, internationalization, services, and throttling.

    This function registers the following middlewares:
    - ConfigMiddleware: Injects configuration into handlers.
    - DBSessionMiddleware: Provides a database session for each handler.
    - SimpleI18nMiddleware: Handles internationalization.
    - ServicesMiddleware: Injects various services like VPN and Plans.
    - ThrottlingMiddleware: Manages rate limiting for user requests.

    Arguments:
        dp (Dispatcher): The main dispatcher instance.
        kwargs (Any): Arbitrary keyword arguments containing middleware dependencies
                      such as config, session, services, and throttling parameters.
    """
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(SimpleI18nMiddleware(kwargs["i18n"]))
    dp.update.outer_middleware.register(
        ServicesMiddleware(
            vpn_service=kwargs["vpn"],
            plans_service=kwargs["plans"],
            promocode_service=kwargs["promocode"],
        )
    )
    dp.update.outer_middleware.register(ThrottlingMiddleware())


__all__ = [
    "register",
]
