from aiogram import Dispatcher

from . import (
    admin_tools,
    download,
    error,
    main_menu,
    payment,
    profile,
    subscription,
    support,
)


def include(dp: Dispatcher) -> None:
    """
    Includes all necessary routers into the main Dispatcher.

    This function registers all the routers for handling different parts of the bot's functionality,
    including error handling, main menu, payment, profile, and subscription management.

    Arguments:
        dp (Dispatcher): The main Dispatcher instance that will handle the routing of updates.
    """
    dp.include_routers(
        *[
            error.router,
            main_menu.router,
            profile.router,
            subscription.router,
            payment.router,
            download.router,
            support.router,
            admin_tools.router,
        ]
    )


__all__ = [
    "include",
]
