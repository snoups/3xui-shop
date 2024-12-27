from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.middlewares import MaintenanceMiddleware
from app.bot.navigation import CreatePromocodeCallback, Navigation


def admin_tools_button() -> InlineKeyboardButton:
    """
    Generates a button for accessing admin tools.

    Returns:
        InlineKeyboardButton: Button to access admin tools.
    """
    return InlineKeyboardButton(text=_("🛠 Admin tools"), callback_data=Navigation.ADMIN_TOOLS)


def admin_tools_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with options for admin tools.

    Includes statistics, user editor, and other management options.

    Returns:
        InlineKeyboardMarkup: Keyboard with admin tool options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistics"),
            callback_data=Navigation.STATISTICS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("👤 Editor users"),
            callback_data=Navigation.EDITOR_USERS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🎟️ Editor promocodes"),
            callback_data=Navigation.EDITOR_PROMOCODES,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("📢 Send notification"),
            callback_data=Navigation.SEND_NOTIFICATION,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("💾 Create backup"),
            callback_data=Navigation.CREATE_BACKUP,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🚧 Maintenance mode"),
            callback_data=Navigation.MAINTENANCE_MODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🔄 Restart bot"),
            callback_data=Navigation.RESTART_BOT,
        )
    )

    builder.row(back_button(Navigation.MAIN_MENU))
    return builder.as_markup()


def editor_promocodes() -> InlineKeyboardMarkup:
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
            callback_data=Navigation.CREATE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🗑️ Delete"),
            callback_data=Navigation.DELETE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("✏️ Edit"),
            callback_data=Navigation.EDIT_PROMOCODE,
        )
    )

    builder.adjust(3)
    builder.row(back_button(Navigation.ADMIN_TOOLS))
    return builder.as_markup()


def promocode_duration_keyboard(callback_data: CreatePromocodeCallback) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for selecting promocode duration.

    Arguments:
        callback_data (CreatePromocodeCallback): Data for tracking promocode creation process.

    Returns:
        InlineKeyboardMarkup: Keyboard for selecting duration options with a back button.
    """
    builder = InlineKeyboardBuilder()
    duration_options = [1, 7, 30, 90, 365]

    for duration in duration_options:
        duration_text = _("1 day", "{} days", duration).format(duration)
        callback_data.duration = duration
        button = InlineKeyboardButton(
            text=duration_text,
            callback_data=callback_data.pack(),
        )
        builder.row(button)

    builder.adjust(2)
    builder.row(back_button(Navigation.CREATE_PROMOCODE))
    return builder.as_markup()


def maintenance_mode_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if MaintenanceMiddleware.active:
        builder.row(
            InlineKeyboardButton(
                text=_("🔴 Turn off"),
                callback_data=Navigation.MAINTENANCE_OFF,
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_("🟢 Turn on"),
                callback_data=Navigation.MAINTENANCE_ON,
            )
        )

    builder.adjust(2)
    builder.row(back_button(Navigation.ADMIN_TOOLS))
    return builder.as_markup()
