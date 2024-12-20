from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavigationAction


def back_button(callback: str) -> InlineKeyboardButton:
    """
    Creates a back button with specified callback data.

    Arguments:
        callback (str): Callback data for handling the back button press.

    Returns:
        InlineKeyboardButton: Inline keyboard button for navigating back.
    """
    return InlineKeyboardButton(text=_("◀️ Back"), callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a single back button.

    Arguments:
        callback (str): Callback data for handling the back button press.

    Returns:
        InlineKeyboardMarkup: Inline keyboard containing a back button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard with a back to main menu button.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a back button to the main menu.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(NavigationAction.MAIN_MENU)]])
