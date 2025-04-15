from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.routers.misc.keyboard import (
    back_button,
    back_to_main_menu_button,
    cancel_button,
)
from app.bot.utils.navigation import NavAdminTools
from app.db.models import Server
from app.db.models.invite import Invite


def admin_tools_keyboard(is_dev: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if is_dev:
        builder.row(
            InlineKeyboardButton(
                text=_("admin_tools:button:server_management"),
                callback_data=NavAdminTools.SERVER_MANAGEMENT,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:statistics"),
            callback_data=NavAdminTools.STATISTICS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:user_editor"),
            callback_data=NavAdminTools.USER_EDITOR,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:invite_editor"),
            callback_data=NavAdminTools.INVITE_EDITOR,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:promocode_editor"),
            callback_data=NavAdminTools.PROMOCODE_EDITOR,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:notification"),
            callback_data=NavAdminTools.NOTIFICATION,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:create_backup"),
            callback_data=NavAdminTools.CREATE_BACKUP,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:maintenance_mode"),
            callback_data=NavAdminTools.MAINTENANCE_MODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:restart_bot"),
            callback_data=NavAdminTools.RESTART_BOT,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("admin_tools:button:test_button"),
            callback_data=NavAdminTools.TEST,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def promocode_editor_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("promocode_editor:button:create"),
            callback_data=NavAdminTools.CREATE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("promocode_editor:button:delete"),
            callback_data=NavAdminTools.DELETE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("promocode_editor:button:edit"),
            callback_data=NavAdminTools.EDIT_PROMOCODE,
        )
    )

    builder.adjust(3)
    builder.row(back_button(NavAdminTools.MAIN))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def promocode_duration_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    duration_options = [1, 7, 30, 90, 365]

    for duration in duration_options:
        duration_text = _("1 day", "{} days", duration).format(duration)
        button = InlineKeyboardButton(
            text=duration_text,
            callback_data=f"{duration}",
        )
        builder.row(button)

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.PROMOCODE_EDITOR))
    return builder.as_markup()


def maintenance_mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    from app.bot.middlewares import MaintenanceMiddleware

    if MaintenanceMiddleware.active:
        builder.row(
            InlineKeyboardButton(
                text=_("maintenance_mode:button:disable"),
                callback_data=NavAdminTools.MAINTENANCE_MODE_DISABLE,
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("maintenance_mode:button:enable"),
                callback_data=NavAdminTools.MAINTENANCE_MODE_ENABLE,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.MAIN))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def servers_keyboard(servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=_("server_management:button:sync"),
            callback_data=NavAdminTools.SYNC_SERVERS,
        )
    )

    builder.add(
        InlineKeyboardButton(
            text=_("server_management:button:add"),
            callback_data=NavAdminTools.ADD_SERVER,
        )
    )

    server: Server
    for server in servers:
        status = "🟢" if server.online else "🔴"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {server.name}",
                callback_data=NavAdminTools.SHOW_SERVER + f"_{server.name}",
            )
        )

    builder.row(back_button(NavAdminTools.MAIN))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def server_keyboard(server_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("server_management:button:ping"),
            callback_data=NavAdminTools.PING_SERVER + f"_{server_name}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("server_management:button:delete"),
            callback_data=NavAdminTools.DELETE_SERVER + f"_{server_name}",
        )
    )

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.SERVER_MANAGEMENT))
    return builder.as_markup()


def confirm_add_server_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("server_management:button:confirm"),
            callback_data=NavAdminTools.СONFIRM_ADD_SERVER,
        )
    )

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.ADD_SERVER_BACK))
    return builder.as_markup()


def notification_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("notification:button:send_to_user"),
            callback_data=NavAdminTools.SEND_NOTIFICATION_USER,
        ),
        InlineKeyboardButton(
            text=_("notification:button:send_to_all"),
            callback_data=NavAdminTools.SEND_NOTIFICATION_ALL,
        ),
    )

    builder.row(
        InlineKeyboardButton(
            text=_("notification:button:last_notification"),
            callback_data=NavAdminTools.LAST_NOTIFICATION,
        )
    )

    builder.row(back_button(NavAdminTools.MAIN))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def last_notification_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text=_("notification:button:edit"),
            callback_data=NavAdminTools.EDIT_NOTIFICATION,
        )
    )

    builder.add(
        InlineKeyboardButton(
            text=_("notification:button:delete"),
            callback_data=NavAdminTools.DELETE_NOTIFICATION,
        )
    )

    builder.row(back_button(NavAdminTools.NOTIFICATION))
    return builder.as_markup()


def confirm_send_notification_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("notification:button:confirm"),
            callback_data=NavAdminTools.CONFIRM_SEND_NOTIFICATION,
        )
    )
    builder.row(cancel_button(NavAdminTools.NOTIFICATION))
    return builder.as_markup()


def invite_editor_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("invite_editor:button:create_invite"),
            callback_data=NavAdminTools.CREATE_INVITE,
        )
    )

    builder.row(
        InlineKeyboardButton(
            text=_("invite_editor:button:list_invites"),
            callback_data=NavAdminTools.LIST_INVITES,
        )
    )

    builder.row(back_button(NavAdminTools.MAIN))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def invite_list_keyboard(
    invites: list[Invite], page: int = 0, limit: int = 5
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    total_invites = len(invites)
    start_idx = page * limit
    end_idx = min(start_idx + limit, total_invites)

    for i in range(start_idx, end_idx):
        invite = invites[i]
        builder.row(
            InlineKeyboardButton(
                text=f"{invite.name} ({invite.clicks} clicks)",
                callback_data=NavAdminTools.SHOW_INVITE_DETAILS + f"_{invite.id}",
            )
        )

    row = []
    if page > 0:
        row.append(
            InlineKeyboardButton(
                text=_("invite_editor:button:previous_page"),
                callback_data=NavAdminTools.SHOW_INVITE_PAGE + f"_{page-1}",
            )
        )

    if (page + 1) * limit < total_invites:
        row.append(
            InlineKeyboardButton(
                text=_("invite_editor:button:next_page"),
                callback_data=NavAdminTools.SHOW_INVITE_PAGE + f"_{page+1}",
            )
        )

    if row:
        builder.row(*row)

    builder.row(back_button(NavAdminTools.INVITE_EDITOR))

    return builder.as_markup()


def invite_details_keyboard(invite: Invite) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if invite.is_active:
        builder.row(
            InlineKeyboardButton(
                text=_("invite_editor:button:disable"),
                callback_data=NavAdminTools.TOGGLE_INVITE_STATUS + f"_{invite.id}",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("invite_editor:button:enable"),
                callback_data=NavAdminTools.TOGGLE_INVITE_STATUS + f"_{invite.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=_("invite_editor:button:delete"),
            callback_data=NavAdminTools.CONFIRM_DELETE_INVITE + f"_{invite.id}",
        )
    )

    builder.row(back_button(NavAdminTools.LIST_INVITES))

    return builder.as_markup()


def confirm_delete_invite_keyboard(invite_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("invite_editor:button:confirm_delete"),
            callback_data=NavAdminTools.DELETE_INVITE + f"_{invite_id}",
        ),
    )
    builder.row(cancel_button(NavAdminTools.SHOW_INVITE_DETAILS + f"_{invite_id}"))
    return builder.as_markup()
