from aiogram import Dispatcher
from aiogram.utils.i18n import SimpleI18nMiddleware

from .config import ConfigMiddleware
from .database import DBSessionMiddleware
from .services import ServicesMiddleware
from .throttling import ThrottlingMiddleware


def register(dp: Dispatcher, **kwargs) -> None:
    """
    Register bot middlewares.

    Arguments:
        dp (Dispatcher): Root router.
        kwargs (Any): Arbitrary keyword arguments.
    """
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(SimpleI18nMiddleware(kwargs["i18n"]))
    dp.update.outer_middleware.register(
        ServicesMiddleware(
            vpn=kwargs["vpn"],
            subscription=kwargs["subscription"],
            promocode=kwargs["promocode"],
        )
    )
    dp.update.outer_middleware.register(ThrottlingMiddleware())


__all__ = [
    "register",
]
