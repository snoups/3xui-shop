import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiohttp.web import HTTPFound, Request, Response

from app.bot.models import ServicesContainer
from app.bot.utils.constants import PREVIOUS_CALLBACK_KEY
from app.bot.utils.misc import parse_redirect_url
from app.bot.utils.navigation import NavDownload
from app.config import Config
from app.db.models import User

from .keyboard import download_keyboard, platforms_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def redirect_to_connection(request: Request) -> Response:
    # TODO: add profile-title=namevpn
    query_string = request.query_string

    if not query_string:
        return Response(status=400, reason="Missing query string.")

    params = parse_redirect_url(query_string)
    app = params.get("app")
    key = params.get("key")

    if not app or not key:
        raise Response(status=400, reason="Invalid parameters.")

    redirect_url = f"{app}://import/{key}#namevpn"
    if app in {"v2raytun", "hiddify"}:  # TODO: hiddify need test
        raise HTTPFound(redirect_url)

    return Response(status=400, reason="Unsupported application.")


@router.callback_query(F.data == NavDownload.MAIN)
async def callback_download(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"User {user.tg_id} opened download apps page.")
    previous_callback = await state.get_value(PREVIOUS_CALLBACK_KEY)
    await callback.message.edit_text(
        text=_("download:message:choose_platform"),
        reply_markup=platforms_keyboard(previous_callback),
    )


@router.callback_query(F.data.startswith(NavDownload.PLATFORM))
async def callback_platform(
    callback: CallbackQuery,
    user: User,
    services: ServicesContainer,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} selected platform: {callback.data}")
    key = await services.vpn.get_key(user)

    match callback.data:
        case NavDownload.PLATFORM_IOS:
            platform = _("download:message:platform_ios")
        case NavDownload.PLATFORM_ANDROID:
            platform = _("download:message:platform_android")
        case _:
            platform = _("download:message:platform_windows")

    await callback.message.edit_text(
        text=_("download:message:connect_to_vpn").format(platform=platform),
        reply_markup=download_keyboard(platform=callback.data, key=key, url=config.bot.HOST),
    )
