from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.localization import localization


def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Generates the main menu keyboard with text localized to the specified language.

    Args:
        lang (str): The language code for localization.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup for the main menu.
    """
    keyboard_texts = localization.get_text("MAIN_MENU_KEYBOARD", lang)

    inline_keyboard = [
        [
            InlineKeyboardButton(text=keyboard_texts["PROFILE"], callback_data="profile"),
            InlineKeyboardButton(text=keyboard_texts["SUBSCRIPTION"], callback_data="subscription"),
        ],
        [
            InlineKeyboardButton(text=keyboard_texts["REFERRAL"], callback_data="referral"),
        ],
        [
            InlineKeyboardButton(text=keyboard_texts["PROMOCODE"], callback_data="promocode"),
        ],
        [
            InlineKeyboardButton(text=keyboard_texts["DOWNLOAD"], callback_data="download"),
        ],
        [
            InlineKeyboardButton(text=keyboard_texts["SUPPORT"], callback_data="support"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
