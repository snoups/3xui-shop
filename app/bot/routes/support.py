import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.support import (
    contact_keyboard,
    how_to_connect_keyboard,
    support_keyboard,
)
from app.bot.navigation import NavigationAction

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavigationAction.SUPPORT, IsPrivate())
async def callback_support(callback: CallbackQuery) -> None:
    """
    Handles the callback query to show the support page.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
    """
    logger.info(f"User {callback.from_user.id} opened support.")
    await callback.message.delete()

    await callback.message.answer(
        text=_(
            "🆘 For collaboration, improvements to functionality, and any other inquiries, "
            "please contact the operator."
        ),
        reply_markup=support_keyboard(),
    )


@router.callback_query(F.data == NavigationAction.HOW_TO_CONNECT, IsPrivate())
async def callback_how_to_connect(callback: CallbackQuery) -> None:
    """
    Handles the callback query to show the instructions on how to connect to the VPN.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
    """
    logger.info(f"User {callback.from_user.id} opened how to connect.")
    await callback.message.delete()

    await callback.message.answer(
        text=_(
            "ℹ️ After subscribing, you will be given an access key "
            "that you can use to connect to our VPN. "
            "If you have a key, go to the application download page and connect the key."
        ),
        reply_markup=how_to_connect_keyboard(),
    )


@router.callback_query(F.data == NavigationAction.VPN_NOT_WORKING, IsPrivate())
async def callback_vpn_not_working(callback: CallbackQuery) -> None:
    """
    Handles the callback query to display VPN troubleshooting information.

    Arguments:
        callback (CallbackQuery): The callback query received from the user.
    """
    logger.info(f"User {callback.from_user.id} opened vpn_not_working.")
    await callback.message.delete()

    await callback.message.answer(
        text=_(
            "ℹ️ There could be several reasons why VPN is not working. "
            "Please check the following:\n\n"
            "- Ensure your internet connection is stable.\n"
            "- Make sure your subscription is active.\n"
            "- Try reconnecting or restarting the app.\n\n"
            "If the issue persists, please contact support."
        ),
        reply_markup=contact_keyboard(),
    )
