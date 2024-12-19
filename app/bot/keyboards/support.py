from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def contact_button() -> InlineKeyboardButton:
    """
    Creates a back button for navigation with specified callback data.

    The button is labeled "← Back" and can be used to navigate to a previous step in the bot.

    Arguments:
        callback (str): Callback data to handle the back button press, usually representing
                        the previous menu or action.

    Returns:
        InlineKeyboardButton: Inline keyboard button that triggers the back action.
    """
    return InlineKeyboardButton(
        text=_("Contact the operator"), url="https://t.me/durov"
    )  # TODO: support id


def support_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for platform selection.

    This keyboard offers options for selecting the platform (iOS, Android, Windows)
    and includes a back button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with platform options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("How to connect"), callback_data=NavigationAction.HOW_TO_CONNECT
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("VPN not working"), callback_data=NavigationAction.VPN_NOT_WORKING
        )
    )
    builder.row(contact_button())

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def how_to_connect_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for platform selection.

    This keyboard offers options for selecting the platform (iOS, Android, Windows)
    and includes a back button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with platform options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("Buy subscription"), callback_data=NavigationAction.SUBSCRIPTION
        )
    )
    builder.row(
        InlineKeyboardButton(text=_("Download app"), callback_data=NavigationAction.DOWNLOAD)
    )
    builder.row(contact_button())

    builder.row(back_button(NavigationAction.SUPPORT))
    return builder.as_markup()


def contact_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for platform selection.

    This keyboard offers options for selecting the platform (iOS, Android, Windows)
    and includes a back button to return to the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with platform options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(contact_button())

    builder.row(back_button(NavigationAction.SUPPORT))
    return builder.as_markup()
