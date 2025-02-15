from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.utils.navigation import NavMain


def close_notification_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=_("misc:button:close_notification"),
        callback_data=NavMain.CLOSE_NOTIFICATION,
    )


def close_notification_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(close_notification_button())
    return builder.as_markup()


def back_button(callback: str, text: str | None = None) -> InlineKeyboardButton:
    if text is None:
        text = _("misc:button:back")
    return InlineKeyboardButton(text=text, callback_data=callback)


def back_keyboard(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_button(callback)]])


def back_to_main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=_("misc:button:back_to_main_menu"),
        callback_data=NavMain.MAIN_MENU,
    )


def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[back_to_main_menu_button()]])


def cancel_button(callback: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_("misc:button:cancel"), callback_data=callback)


def cancel_keyboard(callback: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button(callback)]])
