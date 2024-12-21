from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction, PromocodeCallback


def admin_tools_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=_("🛠 Admin tools"),
        callback_data=NavigationAction.ADMIN_TOOLS,
    )


def admin_tools_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("📊 Statistics"),
            callback_data=NavigationAction.STATISTICS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("👤 Editor users"),
            callback_data=NavigationAction.EDITOR_USERS,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🎟️ Editor promocodes"),
            callback_data=NavigationAction.EDITOR_PROMOCODES,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("📢 Send notification"),
            callback_data=NavigationAction.SEND_NOTIFICATION,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("💾 Create backup"),
            callback_data=NavigationAction.CREATE_BACKUP,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🔄 Restart bot"),
            callback_data=NavigationAction.RESTART_BOT,
        )
    )

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def editor_promocodes() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("Create"),
            callback_data=NavigationAction.CREATE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Delete"),
            callback_data=NavigationAction.DELETE_PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Edit"),
            callback_data=NavigationAction.EDIT_PROMOCODE,
        )
    )

    builder.adjust(3)

    builder.row(back_button(NavigationAction.ADMIN_TOOLS))
    return builder.as_markup()


def promocode_traffic_keyboard(callback_data: PromocodeCallback) -> InlineKeyboardMarkup:
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

    builder.row(back_button(NavigationAction.EDITOR_PROMOCODES))
    return builder.as_markup()


def promocode_duration_keyboard(callback_data: PromocodeCallback) -> InlineKeyboardMarkup:
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

    builder.row(back_button(NavigationAction.CREATE_PROMOCODE))
    return builder.as_markup()
