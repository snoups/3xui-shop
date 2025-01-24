from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.navigation import NavProfile, NavReferral, NavSubscription, NavSupport
from app.bot.routes.admin_tools.keyboard import admin_tools_button


def main_menu_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=_("👤 Profile"), callback_data=NavProfile.MAIN),
        InlineKeyboardButton(text=_("💳 Subscription"), callback_data=NavSubscription.MAIN),
    )
    builder.row(
        InlineKeyboardButton(text=_("👥 Referral Program"), callback_data=NavReferral.MAIN),
        InlineKeyboardButton(text=_("🆘 Support"), callback_data=NavSupport.MAIN),
    )

    if is_admin:
        builder.row(admin_tools_button())

    return builder.as_markup()
