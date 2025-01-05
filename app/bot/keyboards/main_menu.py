from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.admin_tools import admin_tools_button
from app.bot.navigation import NavProfile, NavRefferal, NavSubscription, NavSupport


def main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    """
    Generates the main menu keyboard with navigation options.

    Arguments:
        is_admin (bool): Whether the user is an admin.

    Returns:
        InlineKeyboardMarkup: Main menu keyboard with appropriate options.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=_("👤 Profile"), callback_data=NavProfile.MAIN),
        InlineKeyboardButton(text=_("💳 Subscription"), callback_data=NavSubscription.MAIN),
    )
    builder.row(
        InlineKeyboardButton(text=_("👥 Referral Program"), callback_data=NavRefferal.MAIN),
        InlineKeyboardButton(text=_("🆘 Support"), callback_data=NavSupport.MAIN),
    )

    if is_admin:
        builder.row(admin_tools_button())

    return builder.as_markup()
