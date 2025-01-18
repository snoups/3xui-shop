import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavDownload
from app.bot.services import VPNService

from .keyboard import download_keyboard, platforms_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavDownload.MAIN)
async def callback_download(callback: CallbackQuery) -> None:
    logger.info(f"User {callback.from_user.id} opened download apps page.")
    await callback.message.edit_text(
        text=_("📲 *Choose your platform:*"),
        reply_markup=platforms_keyboard(),
    )


@router.callback_query(F.data.startswith(NavDownload.PLATFORM))
async def callback_platform(callback: CallbackQuery, vpn_service: VPNService) -> None:
    logger.info(f"User {callback.from_user.id} selected platform: {callback.data}")
    key = await vpn_service.get_key(callback.from_user.id)

    if callback.data == NavDownload.PLATFORM_IOS:
        icon = "🍏 "
    elif callback.data == NavDownload.PLATFORM_ANDROID:
        icon = "🤖 "
    else:
        icon = "💻 "

    await callback.message.edit_text(
        text=icon
        + _(
            "To connect, you need to install the app and "
            "enter your key manually or click the `🔌 Connect` button."
        ),
        reply_markup=download_keyboard(callback.data, key),
    )
