from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def pay_keyboard(pay_url) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for payment with a "Pay" button and a back button.

    Arguments:
        pay_url (str): URL to redirect the user to the payment page.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a "Pay" button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_("💸 Pay"), url=pay_url))
    builder.row(back_button(NavigationAction.BACK_TO_PAYMENT))

    return builder.as_markup()
