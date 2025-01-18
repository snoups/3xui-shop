from typing import Any

from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

from .database import DBSessionMiddleware
from .garbage import GarbageMiddleware
from .maintenance import MaintenanceMiddleware
from .throttling import ThrottlingMiddleware


def register(dispatcher: Dispatcher, i18n: I18n, session: async_sessionmaker) -> None:
    """
    Register middlewares to extend the bot's functionality.

    Arguments:
        dispatcher (Dispatcher): Dispatcher instance to register middlewares on.
        i18n (I18n): Instance for internationalization to be used in SimpleI18nMiddleware.
        session (async_sessionmaker): Async session maker to be used by DBSessionMiddleware.
    """

    middlewares = [
        ThrottlingMiddleware(),
        GarbageMiddleware(),
        SimpleI18nMiddleware(i18n),
        MaintenanceMiddleware(),
        DBSessionMiddleware(session),
    ]

    for middleware in middlewares:
        dispatcher.update.outer_middleware.register(middleware)
