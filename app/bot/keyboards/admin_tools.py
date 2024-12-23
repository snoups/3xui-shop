from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
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
    Generates a keyboard with options for admin tools, such as statistics, user editor, and more.

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
            text=_("🔄 Restart bot"),
            callback_data=Navigation.RESTART_BOT,
        )
    )

    builder.row(back_button(Navigation.MAIN_MENU))
    return builder.as_markup()


def editor_promocodes() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with options for managing promocodes, including create, delete, and edit.

    Returns:
        InlineKeyboardMarkup: Keyboard with promocode management options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("Create"),
            callback_data=Navigation.CREATE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Delete"),
            callback_data=Navigation.DELETE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Edit"),
            callback_data=Navigation.EDIT_PROMOCODE,
        )
    )

    builder.adjust(3)
    builder.row(back_button(Navigation.ADMIN_TOOLS))
    return builder.as_markup()


def promocode_traffic_keyboard(callback_data: CreatePromocodeCallback) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for selecting traffic options for a promocode.

    Displays traffic options like 1GB, 5GB, etc., and updates the callback data with value.

    Arguments:
        callback_data (CreatePromocodeCallback): Data for tracking the promocode creation process.

    Returns:
        InlineKeyboardMarkup: Keyboard with traffic selection options and a back button.
    """
    builder = InlineKeyboardBuilder()
    traffic_options = [1, 5, 10, 20, 50, 100]

    for traffic in traffic_options:
        callback_data.traffic = traffic
        button = InlineKeyboardButton(
            text=f"{traffic} " + _("GB"),
            callback_data=callback_data.pack(),
        )
        builder.row(button)

    builder.adjust(2)
    builder.row(back_button(Navigation.EDITOR_PROMOCODES))
    return builder.as_markup()


def promocode_duration_keyboard(callback_data: CreatePromocodeCallback) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for selecting the duration of a promocode.

    Displays duration options like 1 day, 7 days, etc., and updates callback data with value.

    Arguments:
        callback_data (CreatePromocodeCallback): Data for tracking the promocode creation process.

    Returns:
        InlineKeyboardMarkup: Keyboard with duration selection options and a back button.
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
