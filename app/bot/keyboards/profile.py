from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def profile_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for the profile menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup for the profile menu.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("Buy subscription"),
            callback_data=NavigationAction.SUBSCRIPTION,
        )
    )

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()
