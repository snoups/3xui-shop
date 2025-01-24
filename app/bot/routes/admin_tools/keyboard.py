from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.middlewares import MaintenanceMiddleware
from app.bot.navigation import NavAdminTools, NavMain
from app.bot.routes.utils.keyboard import back_button, back_to_main_menu_button
from app.db.models import Server


def admin_tools_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_("🛠 Admin tools"), callback_data=NavAdminTools.MAIN)


def admin_tools_keyboard(is_dev: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if is_dev:
        builder.row(
            InlineKeyboardButton(
                text=_("🌐 Server management"),
                callback_data=NavAdminTools.SERVER_MANAGEMENT,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistics"),
            callback_data=NavAdminTools.STATISTICS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("👤 User editor"),
            callback_data=NavAdminTools.USER_EDITOR,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🎟️ Promocode editor"),
            callback_data=NavAdminTools.PROMOCODE_EDITOR,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("📢 Send notification"),
            callback_data=NavAdminTools.SEND_NOTIFICATION,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("💾 Create backup"),
            callback_data=NavAdminTools.CREATE_BACKUP,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🚧 Maintenance mode"),
            callback_data=NavAdminTools.MAINTENANCE_MODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🔄 Restart bot"),
            callback_data=NavAdminTools.RESTART_BOT,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("TEST BUTTON"),
            callback_data=NavAdminTools.TEST,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def promocode_editor_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("🆕 Create"),
            callback_data=NavAdminTools.CREATE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🗑️ Delete"),
            callback_data=NavAdminTools.DELETE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("✏️ Edit"),
            callback_data=NavAdminTools.EDIT_PROMOCODE,
        )
    )

    builder.adjust(3)
    builder.row(back_button(NavAdminTools.MAIN))
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

    if MaintenanceMiddleware.active:
        builder.row(
            InlineKeyboardButton(
                text=_("🔴 Turn off"),
                callback_data=NavAdminTools.MAINTENANCE_OFF,
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("🟢 Turn on"),
                callback_data=NavAdminTools.MAINTENANCE_ON,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.MAIN))
    return builder.as_markup()


def servers_keyboard(servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("🆕 Add"),
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
    return builder.as_markup()


def server_keyboard(server_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("📶 Ping"),
            callback_data=NavAdminTools.PING_SERVER + f"_{server_name}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🗑️ Delete"),
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
            text=_("✅ Confirm"),
            callback_data=NavAdminTools.СONFIRM_ADD_SERVER,
        )
    )

    builder.adjust(2)
    builder.row(back_button(NavAdminTools.ADD_SERVER_BACK))
    return builder.as_markup()
