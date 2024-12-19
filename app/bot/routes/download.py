import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.download import connect_keyboard, platforms_keyboard
from app.bot.navigation import NavigationAction

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavigationAction.DOWNLOAD, IsPrivate())
async def callback_download(callback: CallbackQuery) -> None:
    """
    Handles the callback when the user selects the download option.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
    """
    logger.info(f"User {callback.from_user.id} opened download apps.")
    await callback.message.delete()
    await callback.message.answer(
        text=_("📲 Choose your platform:"),
        reply_markup=platforms_keyboard(),
    )


@router.callback_query(F.data.startswith(NavigationAction.PLATFORM), IsPrivate())
async def callback_platform(callback: CallbackQuery) -> None:
    """
    Handles the callback when the user selects a platform.

    Arguments:
        callback (CallbackQuery): The callback query from the user.
    """
    logger.info(f"User {callback.from_user.id} selected platform: {callback.data}")
    await callback.message.delete()

    if callback.data == NavigationAction.PLATFORM_IOS:
        icon = "🍏 "
    elif callback.data == NavigationAction.PLATFORM_ANDROID:
        icon = "🤖 "
    else:
        icon = "💻 "
    await callback.message.answer(
        text=icon + _("To connect you need to install the app and enter your key."),
        reply_markup=connect_keyboard(callback.data),  # TODO: connect user key
    )
