from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def back_button(callback: str) -> InlineKeyboardButton:
    """
    Creates a back button for navigation with specified callback data.

    The button is labeled "← Back" and can be used to navigate to a previous step in the bot.

    Arguments:
        callback (str): Callback data to handle the back button press, usually representing
                        the previous menu or action.

    Returns:
        InlineKeyboardButton: Inline keyboard button that triggers the back action.
    """
    return InlineKeyboardButton(text=_("← Back"), callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard containing a single back button with specified callback data.

    This function simplifies the creation of an inline keyboard for navigation, including a
    back button to return to a previous step.

    Arguments:
        callback (str): Callback data to handle the back button press, usually representing
                        the previous menu or action.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with a single back button.
    """
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])
