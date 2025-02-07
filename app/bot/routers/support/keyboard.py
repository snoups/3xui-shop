from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.routers.misc.keyboard import back_button, back_to_main_menu_button
from app.bot.utils.navigation import NavDownload, NavSubscription, NavSupport


def contact_button(support_id: int) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=_("support:button:contact"), url=f"tg://user?id={support_id}")


def support_keyboard(support_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("support:button:how_to_connect"),
            callback_data=NavSupport.HOW_TO_CONNECT,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("support:button:vpn_not_working"),
            callback_data=NavSupport.VPN_NOT_WORKING,
        )
    )

    builder.row(contact_button(support_id))
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def how_to_connect_keyboard(support_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("support:button:buy_subscription"),
            callback_data=NavSubscription.MAIN,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("support:button:download_app"),
            callback_data=NavDownload.MAIN,
        )
    )

    builder.row(contact_button(support_id))
    builder.row(back_button(NavSupport.MAIN))
    return builder.as_markup()


def contact_keyboard(support_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(contact_button(support_id))
    builder.row(back_button(NavSupport.MAIN))
    return builder.as_markup()
