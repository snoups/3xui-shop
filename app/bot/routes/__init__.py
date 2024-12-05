from aiogram import Dispatcher

from . import error, main_menu


def include(dp: Dispatcher) -> None:
    """
    Include bot routers.

    Args:
        dp (Dispatcher): Root router.
    """
    dp.include_routers(
        *[
            error.router,
            main_menu.router,
        ]
    )


__all__ = [
    "include",
]
