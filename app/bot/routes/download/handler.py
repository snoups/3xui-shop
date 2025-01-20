import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User
from aiogram.utils.i18n import gettext as _
from aiohttp.web import HTTPFound, Request, Response

from app.bot.navigation import NavDownload
from app.bot.services import VPNService
from app.config import Config
from app.utils import parse_redirect_url

from .keyboard import download_keyboard, platforms_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def redirect_to_connection(request: Request) -> Response:
    query_string = request.query_string

    if not query_string:
        return Response(status=400, reason="Missing query string.")

    params = parse_redirect_url(query_string)
    app = params.get("app")
    key = params.get("key")

    if not app or not key:
        raise Response(status=400, reason="Invalid parameters.")

    redirect_url = f"{app}://import/{key}"
    if app in {"v2raytun", "hiddify"}:  # TODO: hiddify need test
        raise HTTPFound(redirect_url)

    return Response(status=400, reason="Unsupported application.")


@router.callback_query(F.data == NavDownload.MAIN)
async def callback_download(callback: CallbackQuery, state: FSMContext) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} opened download apps page.")
    previous_callback = await state.get_value("callback")
    await callback.message.edit_text(
        text=_("📲 *Choose your platform:*"),
        reply_markup=platforms_keyboard(previous_callback),
    )


@router.callback_query(F.data.startswith(NavDownload.PLATFORM))
async def callback_platform(
    callback: CallbackQuery,
    vpn_service: VPNService,
    config: Config,
) -> None:
    user: User = callback.from_user
    logger.info(f"User {user.id} selected platform: {callback.data}")
    key = await vpn_service.get_key(user.id)

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
        reply_markup=download_keyboard(platform=callback.data, key=key, url=config.bot.WEBHOOK),
    )
