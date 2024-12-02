from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.localization import localization


def get_back_button(lang: str, callback: str) -> InlineKeyboardButton:
    """
    Creates a "Back" button with localized text.

    Args:
        lang (str): The language code for localization.
        callback (str): The callback data for the button.

    Returns:
        InlineKeyboardButton: The "Back" button.
    """
    back = localization.get_text("BACK_BUTTON", lang)
    return InlineKeyboardButton(text=back, callback_data=callback)


def get_back_keyboard(lang: str, callback: str) -> InlineKeyboardMarkup:
    """
    Creates a keyboard containing only a single "Back" button.

    Args:
        lang (str): The language code for localization.
        callback (str): The callback data for the "Back" button.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup with the "Back" button.
    """
    inline_keyboard = [[get_back_button(lang, callback)]]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
