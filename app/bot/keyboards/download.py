from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def platforms_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for platform selection.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with platform options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🍏 IOS", callback_data=NavigationAction.PLATFORM_IOS),
        InlineKeyboardButton(text="🤖 Android", callback_data=NavigationAction.PLATFORM_ANDROID),
        InlineKeyboardButton(text="💻 Windows", callback_data=NavigationAction.PLATFORM_WINDOWS),
    )

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def connect_keyboard(platform: NavigationAction, key: str) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for connecting to a VPN based on the platform.

    Arguments:
        platform (NavigationAction): The platform to determine the correct link.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with download and connect options, and a back button.
    """
    builder = InlineKeyboardBuilder()

    # v2raytun://import/ | hiddify://import/
    if platform == NavigationAction.PLATFORM_IOS:
        download = "https://apps.apple.com/ru/app/v2raytun/id6476628951"
        connect = f"https://tinyurl.com/bbpy5bx7/{key}"
    elif platform == NavigationAction.PLATFORM_ANDROID:
        download = "https://play.google.com/store/apps/details?id=com.v2raytun.android"
        connect = f"https://tinyurl.com/bbpy5bx7/{key}"
    else:
        download = (
            "https://github.com/hiddify/hiddify-next/releases/download/"
            + "v2.0.5/Hiddify-Windows-Setup-x64.exe"
        )
        connect = f"https://tinyurl.com/5cea6ra4{key}"

    builder.row(
        InlineKeyboardButton(text=_("Download"), url=download),
        InlineKeyboardButton(text=_("Connect"), url=connect),
    )

    builder.row(back_button(NavigationAction.DOWNLOAD))
    return builder.as_markup()
