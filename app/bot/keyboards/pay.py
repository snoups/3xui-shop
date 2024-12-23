from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import Navigation, SubscriptionCallback


def pay_keyboard(pay_url: str, callback_data: SubscriptionCallback) -> InlineKeyboardMarkup:
    """
    Generates a payment keyboard with a link to the payment URL and a back button.

    This keyboard is designed for users to initiate a payment. It includes a button
    with the specified payment URL and a back button to navigate to the duration selection menu.

    Arguments:
        pay_url (str): URL to redirect the user to the payment page.
        callback_data (SubscriptionCallback): Callback data to identify the navigation state.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a pay button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_("💸 Pay"), url=pay_url))

    callback_data.state = Navigation.DURATION
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()
