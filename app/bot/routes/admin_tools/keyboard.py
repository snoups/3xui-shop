from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.middlewares import MaintenanceMiddleware
from app.bot.navigation import NavAdminTools, NavMain
from app.bot.routes.utils.keyboard import back_button
from app.db.models import Server


def admin_tools_button() -> InlineKeyboardButton:
    """
    Generates a button for accessing admin tools.

    Returns:
        InlineKeyboardButton: Button to access admin tools.
    """
    return InlineKeyboardButton(text=_("🛠 Admin tools"), callback_data=NavAdminTools.MAIN)


def admin_tools_keyboard(is_dev: bool) -> InlineKeyboardMarkup:
    """
    Generates a keyboard with options for admin tools.

    Includes statistics, user editor, and other management options.

    Arguments:
        is_dev (bool): Whether the user is a developer, showing additional management options.

    Returns:
        InlineKeyboardMarkup: Keyboard with admin tool options and a back button.
    """
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

    builder.row(back_button(NavMain.MAIN_MENU))
    return builder.as_markup()


def promocode_editor_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard for managing promocodes.

    Options include create, delete, and edit promocodes, with a back button.

    Returns:
        InlineKeyboardMarkup: Keyboard with promocode management options and a back button.
    """
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
    """
    Generates a keyboard for selecting promocode duration.

    Returns:
        InlineKeyboardMarkup: Keyboard for selecting duration options with a back button.
    """
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
    """
    Generates a keyboard for toggling maintenance mode.

    Returns:
        InlineKeyboardMarkup: Keyboard with maintenance mode toggle and a back button.
    """
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
    """
    Generates a keyboard for managing servers.

    Options include adding, deleting, and editing servers, with a back button.

    Arguments:
        servers (list): List of server objects to be displayed in the keyboard.

    Returns:
        InlineKeyboardMarkup: Keyboard with server management options and a back button.
    """
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
    """
    Generates a keyboard for a single server with options for pinging and deleting it.

    Arguments:
        server_name (str): The name of the server for which the keyboard is generated.

    Returns:
        InlineKeyboardMarkup: Keyboard with server options (ping and delete) and a back button.
    """
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
    """
    Generates a confirmation keyboard for adding a server.

    Returns:
        InlineKeyboardMarkup: Keyboard with a confirmation button and a back button.
    """
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
