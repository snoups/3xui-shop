from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generates the main menu keyboard.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup for the main menu.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text=_("👤 Profile"), callback_data="profile"),
        InlineKeyboardButton(text=_("💳 Subscription"), callback_data="subscription"),
    )

    builder.row(InlineKeyboardButton(text=_("👥 Referral Program"), callback_data="referral"))
    builder.row(InlineKeyboardButton(text=_("🏷 Activate Promo Code"), callback_data="promocode"))
    builder.row(InlineKeyboardButton(text=_("📲 Download App"), callback_data="download"))
    builder.row(InlineKeyboardButton(text=_("🆘 Support"), callback_data="support"))

    return builder.as_markup()
