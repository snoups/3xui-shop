from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.routers.misc.keyboard import back_to_main_menu_button
from app.bot.utils.navigation import NavDownload


def referral_keyboard(connect: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if connect:
        builder.row(
            InlineKeyboardButton(
                text=_("subscription:button:connect"),
                callback_data=NavDownload.MAIN,
            )
        )
    builder.row(back_to_main_menu_button())

    return builder.as_markup()
