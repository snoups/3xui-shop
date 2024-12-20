from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.keyboards.subscription import buy_subscription_button
from app.bot.navigation import NavigationAction


def buy_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for the user profile menu.

    This keyboard includes an option to buy a subscription and a back button
    to return to the main menu.

    Returns:
        InlineKeyboardMarkup: The inline keyboard with the buy subscription option and back button.
    """
    builder = InlineKeyboardBuilder()
    builder.row(buy_subscription_button())
    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def show_key_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for showing the user's key.

    This keyboard includes an option to show the user's key and a back button
    to return to the main menu.

    Returns:
        InlineKeyboardMarkup: The inline keyboard with the show key option and back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("🔑 Show key"),
            callback_data=NavigationAction.SHOW_KEY,
        )
    )

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()
