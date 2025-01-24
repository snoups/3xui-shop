import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsDev
from app.bot.navigation import NavAdminTools
from app.bot.services.vpn import VPNService
from app.db.models import User

from .keyboard import admin_tools_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.MAIN, IsAdmin())
async def callback_admin_tools(callback: CallbackQuery, user: User) -> None:
    logger.info(f"Admin {user.tg_id} opened admin tools.")
    is_dev = await IsDev()(callback)
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(is_dev),
    )


from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Transaction


@router.callback_query(F.data == NavAdminTools.TEST, IsAdmin())
async def callback_admin_tools(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    vpn_service: VPNService,
) -> None:
    logger.info(f"Admin {user.tg_id} clicked TEST BUTTON.")
    logger.info(
        f"{user}\n\n{user.transactions}\n\n{user.server}\n\n{user.activated_promocodes}\n\n"
    )
    logger.info(f"{await vpn_service.get_key(user.tg_id)}\n\n")

    server, api = vpn_service.server_service.servers[1]
    logger.info(f"{server}\n\n{server.users}\n\n")

    transaction = await Transaction.get(session=session, payment_id="test")
    logger.info(f"{transaction}\n\n{transaction.user}")
