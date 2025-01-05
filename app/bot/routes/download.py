import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.download import download_keyboard, platforms_keyboard
from app.bot.navigation import NavDownload
from app.bot.services import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavDownload.MAIN, IsPrivate())
async def callback_download(callback: CallbackQuery) -> None:
    """
    Handler for opening the platform selection menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"User {callback.from_user.id} opened download apps page.")
    await callback.message.edit_text(
        text=_("📲 *Choose your platform:*"),
        reply_markup=platforms_keyboard(),
    )


@router.callback_query(F.data.startswith(NavDownload.PLATFORM), IsPrivate())
async def callback_platform(callback: CallbackQuery, vpn_service: VPNService) -> None:
    """
    Handler for selecting a platform and providing the VPN key.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        vpn_service (VPNService): Service for managing VPN keys.
    """
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
