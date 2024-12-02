from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.back_keyboard import get_back_button
from bot.utils import subscriptions
from bot.utils.localization import localization


def get_subscription_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Generates the subscription keyboard with text localized to the specified language.

    Args:
        lang (str): The language code for localization.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup for the subscription menu.
    """
    size = localization.get_text("SIZES.GIGABYTES", lang)
    day = localization.get_text("SIZES.GIGABYTES", lang)
    plans = subscriptions.get()
    builder = InlineKeyboardBuilder()

    for p in plans:
        builder.row(
            InlineKeyboardButton(
                text=p["plan"] + " " + size + " / " + day, callback_data=p["callback"]
            )
        )

    builder.adjust(2)
    builder.row(get_back_button(lang, "main_menu"))
    return builder.as_markup()
