from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def back_button(callback: str) -> InlineKeyboardButton:
    """
    Creates a back button for navigation.

    Arguments:
        callback (str): Callback data for handling the back button press.

    Returns:
        InlineKeyboardButton: Inline keyboard button for the back action.
    """
    return InlineKeyboardButton(text=_("← Back"), callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a single back button.

    Arguments:
        callback (str): Callback data for handling the back button press.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup containing the back button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])
