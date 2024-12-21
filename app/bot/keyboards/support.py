from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction


def contact_button(support_id: int) -> InlineKeyboardButton:
    """
    Creates a contact button to reach the operator via Telegram.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardButton: Inline keyboard button with a URL to contact the operator.
    """
    return InlineKeyboardButton(
        text=_("👨‍💻 Contact the operator"), url=f"tg://user?id={support_id}"
    )


def support_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for support-related actions.

    This keyboard provides options for users to get help with connecting, report
    VPN issues, contact the support operator, and return to the main menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with support options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("❓ How to connect"), callback_data=NavigationAction.HOW_TO_CONNECT
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("❓ VPN not working"), callback_data=NavigationAction.VPN_NOT_WORKING
        )
    )
    builder.row(contact_button(support_id))

    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def how_to_connect_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for users seeking connection instructions.

    This keyboard includes options for buying a subscription, downloading the app,
    contacting support, and returning to the previous support menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with connection help options and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("💳 Buy subscription"), callback_data=NavigationAction.SUBSCRIPTION
        )
    )
    builder.row(
        InlineKeyboardButton(text=_("📥 Download app"), callback_data=NavigationAction.DOWNLOAD)
    )
    builder.row(contact_button(support_id))

    builder.row(back_button(NavigationAction.SUPPORT))
    return builder.as_markup()


def contact_keyboard(support_id: int) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for contacting support.

    This keyboard includes a button for contacting the support operator and a back button
    to return to the previous support menu.

    Arguments:
        support_id (int): Telegram user ID of the support operator.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with the contact button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(contact_button(support_id))

    builder.row(back_button(NavigationAction.SUPPORT))
    return builder.as_markup()
