from aiogram import Dispatcher

from . import error, main_menu, profile, subscription


def include(dp: Dispatcher) -> None:
    """
    Include bot routers.

    Arguments:
        dp (Dispatcher): Root router.
    """
    dp.include_routers(
        *[
            error.router,
            main_menu.router,
            profile.router,
            subscription.router,
        ]
    )


__all__ = [
    "include",
]
