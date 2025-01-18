from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.navigation import NavMain, NavProfile, NavSubscription
from app.bot.routes.utils.keyboard import back_button


def buy_subscription_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("💳 Buy subscription"),
            callback_data=NavSubscription.MAIN,
        )
    )

    builder.row(back_button(NavMain.MAIN_MENU))
    return builder.as_markup()


def show_key_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("🔑 Show key"),
            callback_data=NavProfile.SHOW_KEY,
        )
    )

    builder.row(back_button(NavMain.MAIN_MENU))
    return builder.as_markup()
