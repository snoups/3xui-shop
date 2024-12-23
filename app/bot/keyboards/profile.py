from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import Navigation


def buy_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard for purchasing a subscription.

    This keyboard allows the user to navigate to the subscription purchase page.
    It includes a button for subscription purchase and a back button for returning
    to the main menu.

    Returns:
        InlineKeyboardMarkup: Keyboard with a subscription button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("💳 Buy subscription"),
            callback_data=Navigation.SUBSCRIPTION,
        )
    )

    builder.row(back_button(Navigation.MAIN_MENU))
    return builder.as_markup()


def show_key_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard to display the user's VPN access key.

    This keyboard provides a button for showing the VPN key and a back button to return
    to the main menu. It is intended for users to retrieve their key after subscription.

    Returns:
        InlineKeyboardMarkup: Keyboard with options to show the key and go back.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("🔑 Show key"),
            callback_data=Navigation.SHOW_KEY,
        )
    )

    builder.row(back_button(Navigation.MAIN_MENU))
    return builder.as_markup()
