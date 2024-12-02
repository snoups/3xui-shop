from aiogram import Dispatcher

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
    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["session"]))
    dp.update.outer_middleware.register(ConfigMiddleware(kwargs["config"]))
    dp.update.outer_middleware.register(ThrottlingMiddleware())


__all__ = [
    "register",
]
