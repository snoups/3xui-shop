from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.admin_tools import admin_tools_button
from app.bot.navigation import NavigationAction


def main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for the main menu with various user options.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with buttons for main menu options.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("👤 Profile"),
            callback_data=NavigationAction.PROFILE,
        ),
        InlineKeyboardButton(
            text=_("💳 Subscription"),
            callback_data=NavigationAction.SUBSCRIPTION,
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=_("👥 Referral Program"),
            callback_data=NavigationAction.REFERRAL,
        ),
        InlineKeyboardButton(
            text=_("🆘 Support"),
            callback_data=NavigationAction.SUPPORT,
        ),
    )

    if is_admin:
        builder.row(admin_tools_button())

    return builder.as_markup()
