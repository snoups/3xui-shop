from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


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
            text=_("👤 Editor user"),
            callback_data=NavigationAction.EDITOR_USER,
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
