from aiogram import Dispatcher

from . import (
    admin_tools,
    download,
    error,
    main_menu,
    notification,
    profile,
    referral,
    subscription,
    support,
)


def include(dp: Dispatcher) -> None:
    """
    Includes all necessary routers into the main Dispatcher.

    Arguments:
        dp (Dispatcher): The main Dispatcher instance that will handle the routing of updates.
    """
    dp.include_routers(
        *[
            error.router,
            admin_tools.router,
            download.router,
            main_menu.router,
            notification.router,
            profile.router,
            referral.router,
            subscription.router,
            support.router,
        ]
    )


__all__ = [
    "include",
]
