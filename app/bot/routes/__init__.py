from aiogram import Dispatcher

from . import error, inline, private


def include(dp: Dispatcher) -> None:
    """
    Include bot routers.

    Args:
        dp (Dispatcher): Root router.
    """
    dp.include_routers(
        *[
            error.router,
            private.command.router,
            private.callback.router,
            inline.router,
        ]
    )


__all__ = [
    "include",
]
