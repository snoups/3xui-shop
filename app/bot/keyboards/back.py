from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def back_button(callback: str) -> InlineKeyboardButton:
    """
    Creates a "Back" button.

    Args:
        callback (str): The callback data for the button.

    Returns:
        InlineKeyboardButton: The "Back" button.
    """
    return InlineKeyboardButton(text=_("Back"), callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard containing only a single "Back" button.

    Args:
        callback (str): The callback data for the "Back" button.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup with the "Back" button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])
