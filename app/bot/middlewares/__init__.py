from aiogram import Dispatcher
from aiogram.utils.i18n import SimpleI18nMiddleware

from .config import ConfigMiddleware
from .database import DBSessionMiddleware
from .garbage import GarbageMiddleware
from .maintenance import MaintenanceMiddleware
from .services import ServicesMiddleware
from .throttling import ThrottlingMiddleware


def register(dp: Dispatcher, **kwargs) -> None:
    """
    Register middlewares to extend the bot's functionality.

    Arguments:
        dp (Dispatcher): Dispatcher instance to register middlewares on.
        kwargs (Any): Middleware dependencies such as config, session, services, and throttling.
    """
    dp.update.outer_middleware.register(ThrottlingMiddleware())
    dp.update.outer_middleware.register(GarbageMiddleware())
    dp.update.outer_middleware.register(SimpleI18nMiddleware(kwargs["i18n"]))
    dp.update.outer_middleware.register(MaintenanceMiddleware())
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(ServicesMiddleware(**kwargs["services"]))


__all__ = [
    "register",
]
