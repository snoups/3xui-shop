import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.utils.navigation import NavSupport
from app.config import Config
from app.db.models import User

from .keyboard import contact_keyboard, how_to_connect_keyboard, support_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavSupport.MAIN)
async def callback_support(callback: CallbackQuery, user: User, config: Config) -> None:
    logger.info(f"User {user.tg_id} opened support page.")
    await callback.message.edit_text(
        text=_("support:message:main"),
        reply_markup=support_keyboard(config.bot.SUPPORT_ID),
    )


@router.callback_query(F.data == NavSupport.HOW_TO_CONNECT)
async def callback_how_to_connect(callback: CallbackQuery, user: User, config: Config) -> None:
    logger.info(f"User {user.tg_id} opened how to connect page.")
    await callback.message.edit_text(
        text=_("support:message:how_to_connect"),
        reply_markup=how_to_connect_keyboard(config.bot.SUPPORT_ID),
    )


@router.callback_query(F.data == NavSupport.VPN_NOT_WORKING)
async def callback_vpn_not_working(callback: CallbackQuery, user: User, config: Config) -> None:
    logger.info(f"User {user.tg_id} opened vpn not working page.")
    await callback.message.edit_text(
        text=_("support:message:vpn_not_working"),
        reply_markup=contact_keyboard(config.bot.SUPPORT_ID),
    )
