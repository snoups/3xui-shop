from aiogram import Dispatcher
from aiohttp.web import Application

from app.bot.utils.constants import CONNECTION_WEBHOOK

from . import (
    admin_tools,
    download,
    main_menu,
    misc,
    profile,
    referral,
    subscription,
    support,
)


def include(app: Application, dispatcher: Dispatcher) -> None:
    app.router.add_get(CONNECTION_WEBHOOK, download.handler.redirect_to_connection)
    dispatcher.include_routers(
        misc.error_handler.router,
        misc.notification_handler.router,
        main_menu.handler.router,
        profile.handler.router,
        referral.handler.router,
        support.handler.router,
        download.handler.router,
        subscription.subscription_handler.router,
        subscription.payment_handler.router,
        subscription.promocode_handler.router,
        subscription.trial_handler.router,
        admin_tools.admin_tools_handler.router,
        admin_tools.backup_handler.router,
        admin_tools.invites_handler.router,
        admin_tools.maintenance_handler.router,
        admin_tools.notification_handler.router,
        admin_tools.promocode_handler.router,
        admin_tools.restart_handler.router,
        admin_tools.server_handler.router,
        admin_tools.statistics_handler.router,
        admin_tools.user_handler.router,
    )
