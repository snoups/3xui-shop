from aiogram import Dispatcher

from . import admin_tools, download, main_menu, profile, referral, support, utils
from .subscription import payment_handler, promocode_handler, subscription_handler


def include(dp: Dispatcher) -> None:
    """
    Includes all necessary routers into the main Dispatcher.

    Arguments:
        dp (Dispatcher): The main Dispatcher instance that will handle the routing of updates.
    """
    dp.include_routers(
        *[
            utils.error_handler.router,
            utils.notification_handler.router,
            #
            main_menu.handler.router,
            profile.handler.router,
            referral.handler.router,
            support.handler.router,
            download.handler.router,
            #
            subscription_handler.router,
            payment_handler.router,
            promocode_handler.router,
            #
            admin_tools.admin_tools_handler.router,
            admin_tools.backup_handler.router,
            admin_tools.maintenance_handler.router,
            admin_tools.notification_handler.router,
            admin_tools.promocode_handler.router,
            admin_tools.restart_handler.router,
            admin_tools.server_handler.router,
            admin_tools.statistics_handler.router,
            admin_tools.user_handler.router,
        ]
    )


__all__ = [
    "include",
]
