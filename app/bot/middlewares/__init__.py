from aiogram import Dispatcher
from aiogram.utils.i18n import SimpleI18nMiddleware

from .api import ApiMiddleware
from .config import ConfigMiddleware
from .database import DBSessionMiddleware
from .throttling import ThrottlingMiddleware


def register(dp: Dispatcher, **kwargs) -> None:
    """
    Register bot middlewares.

    Args:
        dp (Dispatcher): Root router.
        kwargs (Any): Arbitrary keyword arguments.
    """
    dp.update.outer_middleware.register(ApiMiddleware(kwargs["api"]))
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(ThrottlingMiddleware())
    dp.update.outer_middleware.register(SimpleI18nMiddleware(kwargs["i18n"]))


__all__ = [
    "register",
]
