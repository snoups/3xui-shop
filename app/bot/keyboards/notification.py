from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.navigation import NavMain


def close_notification_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard with a single button to close the notification.

    Returns:
        InlineKeyboardMarkup: Keyboard with a close button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("💥 Close"),
            callback_data=NavMain.CLOSE_NOTIFICATION,
        )
    )

    return builder.as_markup()
