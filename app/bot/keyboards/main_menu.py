from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.admin_tools import admin_tools_button
from app.bot.navigation import Navigation


def main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """
    Generates the main menu keyboard with navigation options.

    Includes options for the profile, subscription, referral program, support,
    and admin tools if the user is an admin.

    Arguments:
        is_admin (bool): Whether the user is an admin.

    Returns:
        InlineKeyboardMarkup: Main menu keyboard with appropriate options.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=_("👤 Profile"), callback_data=Navigation.PROFILE),
        InlineKeyboardButton(text=_("💳 Subscription"), callback_data=Navigation.SUBSCRIPTION),
    )
    builder.row(
        InlineKeyboardButton(text=_("👥 Referral Program"), callback_data=Navigation.REFERRAL),
        InlineKeyboardButton(text=_("🆘 Support"), callback_data=Navigation.SUPPORT),
    )

    if is_admin:
        builder.row(admin_tools_button())

    return builder.as_markup()
