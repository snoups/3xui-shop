from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.navigation import NavigationAction


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with main menu options.
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
            callback_data=NavigationAction.REFERAL,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🏷 Activate Promo Code"),
            callback_data=NavigationAction.PROMOCODE,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("📲 Download App"),
            callback_data=NavigationAction.DOWNLOAD,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("🆘 Support"),
            callback_data=NavigationAction.SUPPORT,
        )
    )

    return builder.as_markup()
