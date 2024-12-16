from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def profile_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for the user's profile menu.

    This keyboard provides options for the user to buy a subscription and a back button
    to return to the main menu.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup for the profile menu with options
        and a back button.
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
