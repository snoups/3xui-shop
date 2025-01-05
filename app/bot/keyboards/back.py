from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavMain


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
        InlineKeyboardMarkup: Keyboard with a back button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    """
    Generates a button to return to the main menu.

    Returns:
        InlineKeyboardButton: Button to go back to the main menu.
    """
    return InlineKeyboardButton(text=_("◀️ Back to main menu"), callback_data=NavMain.MAIN_MENU)


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with a button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: Keyboard with the back-to-main-menu button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])


def cancel_button(callback: str) -> InlineKeyboardButton:
    """
    Generates a button to cancel the current action.

    Arguments:
        callback (str): The callback data to cancel the action.

    Returns:
        InlineKeyboardButton: Button to cancel the current action.
    """
    return InlineKeyboardButton(text=_("◀️ Cancel"), callback_data=callback)


def cancel_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Generates a keyboard with a single cancel button.

    Arguments:
        callback (str): The callback data for the cancel button.

    Returns:
        InlineKeyboardMarkup: Keyboard with a cancel button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button(callback)]])
