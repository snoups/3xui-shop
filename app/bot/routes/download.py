import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.download import download_keyboard, platforms_keyboard
from app.bot.navigation import Navigation
from app.bot.services.vpn import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == Navigation.DOWNLOAD, IsPrivate())
async def callback_download(callback: CallbackQuery) -> None:
    logger.info(f"User {callback.from_user.id} opened download apps.")
    await callback.message.edit_text(
        text=_("📲 *Choose your platform:*"),
        reply_markup=platforms_keyboard(),
    )


@router.callback_query(F.data.startswith(Navigation.PLATFORM), IsPrivate())
async def callback_platform(callback: CallbackQuery, vpn_service: VPNService) -> None:
    logger.info(f"User {callback.from_user.id} selected platform: {callback.data}")
    key = await vpn_service.get_key(callback.from_user.id)

    if callback.data == Navigation.PLATFORM_IOS:
        icon = "🍏 "
    elif callback.data == Navigation.PLATFORM_ANDROID:
        icon = "🤖 "
    else:
        icon = "💻 "

    await callback.message.edit_text(
        text=icon + _("To connect you need to install the app and enter your key."),
        reply_markup=download_keyboard(callback.data, key),
    )
