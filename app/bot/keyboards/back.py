from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import Navigation


def back_button(callback: str) -> InlineKeyboardButton:
    """
    Generates a button to go back to the previous menu.

    Arguments:
        callback (str): The callback data to navigate back.

    Returns:
        InlineKeyboardButton: Button to go back to the previous menu.
    """
    return InlineKeyboardButton(text=_("◀️ Back"), callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Generates a keyboard with a single back button.

    Arguments:
        callback (str): The callback data for the back button.

    Returns:
        InlineKeyboardMarkup: Keyboard with the back button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    """
    Generates a button to return to the main menu.

    Returns:
        InlineKeyboardButton: Button to go back to the main menu.
    """
    return InlineKeyboardButton(text=_("◀️ Back to main menu"), callback_data=Navigation.MAIN_MENU)


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with a button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: Keyboard with the back-to-main-menu button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])
