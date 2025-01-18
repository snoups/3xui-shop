import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavSupport
from app.config import Config

from .keyboard import contact_keyboard, how_to_connect_keyboard, support_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavSupport.MAIN)
async def callback_support(callback: CallbackQuery, config: Config) -> None:
    logger.info(f"User {callback.from_user.id} opened support page.")
    await callback.message.edit_text(
        text=_(
            "🆘 *Support:*\n"
            "\n"
            "For collaboration, improvements to functionality, and any other inquiries, "
            "please contact the operator."
        ),
        reply_markup=support_keyboard(config.bot.SUPPORT_ID),
    )


@router.callback_query(F.data == NavSupport.HOW_TO_CONNECT)
async def callback_how_to_connect(callback: CallbackQuery, config: Config) -> None:
    logger.info(f"User {callback.from_user.id} opened how to connect page.")
    await callback.message.edit_text(
        text=_(
            "ℹ️ *How to connect:*\n"
            "\n"
            "After subscribing, you will be given an access key "
            "that you can use to connect to our VPN. "
            "If you have a key, go to the application download page and connect the key."
        ),
        reply_markup=how_to_connect_keyboard(config.bot.SUPPORT_ID),
    )


@router.callback_query(F.data == NavSupport.VPN_NOT_WORKING)
async def callback_vpn_not_working(callback: CallbackQuery, config: Config) -> None:
    logger.info(f"User {callback.from_user.id} opened vpn not working page.")
    await callback.message.edit_text(
        text=_(
            "ℹ️ *VPN not working:*\n"
            "\n"
            "There could be several reasons why VPN is not working. "
            "Please check the following:\n"
            "\n"
            "- Ensure your internet connection is stable.\n"
            "- Make sure your subscription is active.\n"
            "- Try reconnecting or restarting the app.\n"
            "\n"
            "If the issue persists, please contact support."
        ),
        reply_markup=contact_keyboard(config.bot.SUPPORT_ID),
    )
