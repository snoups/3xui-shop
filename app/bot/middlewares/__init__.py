from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

from .database import DBSessionMiddleware
from .garbage import GarbageMiddleware
from .maintenance import MaintenanceMiddleware
from .throttling import ThrottlingMiddleware


def register(dispatcher: Dispatcher, i18n: I18n, session: async_sessionmaker) -> None:
    middlewares = [
        ThrottlingMiddleware(),
        GarbageMiddleware(),
        SimpleI18nMiddleware(i18n),
        MaintenanceMiddleware(),
        DBSessionMiddleware(session),
    ]

    for middleware in middlewares:
        dispatcher.update.middleware.register(middleware)
