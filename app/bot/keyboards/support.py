from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import Navigation


def contact_button(support_id: int) -> InlineKeyboardButton:
    """
    Generates a button for contacting the support operator via Telegram.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardButton: Button linking to the support operator's Telegram profile.
    """
    return InlineKeyboardButton(
        text=_("👨‍💻 Contact the operator"), url=f"tg://user?id={support_id}"
    )


def support_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates a keyboard with support options, including common issues and direct contact.

    Users can select predefined support topics or contact the support operator directly.
    A back button allows navigation back to the main menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Keyboard with support options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("❓ How to connect"),
            callback_data=Navigation.HOW_TO_CONNECT,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("❓ VPN not working"),
            callback_data=Navigation.VPN_NOT_WORKING,
        )
    )
    builder.row(contact_button(support_id))

    builder.row(back_button(Navigation.MAIN_MENU))
    return builder.as_markup()


def how_to_connect_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates a keyboard with instructions for connecting to the VPN and contacting support.

    Includes options to purchase a subscription, download the app, and contact the operator.
    A back button navigates to the support menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Keyboard with connection instructions and support options.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("💳 Buy subscription"),
            callback_data=Navigation.SUBSCRIPTION,
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("📥 Download app"),
            callback_data=Navigation.DOWNLOAD,
        )
    )
    builder.row(contact_button(support_id))

    builder.row(back_button(Navigation.SUPPORT))
    return builder.as_markup()


def contact_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for contacting the support operator.

    Displays a button to contact the operator directly and a back button to the support menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Keyboard with the contact button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(contact_button(support_id))

    builder.row(back_button(Navigation.SUPPORT))
    return builder.as_markup()
