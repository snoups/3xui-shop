import asyncio
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.keyboards.admin_tools import (
    admin_tools_keyboard,
    editor_promocodes,
    promocode_duration_keyboard,
    promocode_traffic_keyboard,
)
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import NavigationAction, PromocodeCallback, States
from app.bot.services.promocode import PromocodeService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class DeletePromocodeStates(StatesGroup):
    waiting_for_promocode = State()


@router.callback_query(F.data == NavigationAction.ADMIN_TOOLS, IsPrivate(), IsAdmin())
async def callback_statistics(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened admin tools.")
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(),
    )


@router.callback_query(F.data == NavigationAction.STATISTICS, IsPrivate(), IsAdmin())
async def callback_statistics(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened statistics.")
    pass


@router.callback_query(F.data == NavigationAction.EDITOR_USERS, IsPrivate(), IsAdmin())
async def callback_editor_users(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened editor users.")
    pass


@router.callback_query(F.data == NavigationAction.EDITOR_PROMOCODES, IsPrivate(), IsAdmin())
async def callback_editor_promocodes(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"Admin {callback.from_user.id} opened editor promocodes.")
    await state.clear()
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*"),
        reply_markup=editor_promocodes(),
    )


@router.callback_query(F.data == NavigationAction.SEND_NOTIFICATION, IsPrivate(), IsAdmin())
async def callback_send_notification(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} opened send notification.")
    pass


@router.callback_query(F.data == NavigationAction.CREATE_BACKUP, IsPrivate(), IsAdmin())
async def callback_create_backup(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} created backup.")
    pass


@router.callback_query(F.data == NavigationAction.RESTART_BOT, IsPrivate(), IsAdmin())
async def callback_restart_bot(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} restarted bot.")
    pass


# region: Create Promocode
@router.callback_query(F.data == NavigationAction.CREATE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_create_promocode(callback: CallbackQuery) -> None:
    logger.info(f"Admin {callback.from_user.id} started creating promocode.")
    data = PromocodeCallback(state=States.TRAFFIC)
    traffic_keyboard = promocode_traffic_keyboard(data)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n" "\n" "_Select the traffic volume_"),
        reply_markup=traffic_keyboard,
    )


@router.callback_query(IsPrivate(), IsAdmin(), PromocodeCallback.filter(F.state == States.TRAFFIC))
async def choose_traffic(callback: CallbackQuery, callback_data: PromocodeCallback) -> None:
    logger.info(f"Admin {callback.from_user.id} selected {callback_data.traffic} GB for promocode.")
    callback_data.state = States.DURATION
    duration_keyboard = promocode_duration_keyboard(callback_data)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n" "\n" "_Specify the duration_"),
        reply_markup=duration_keyboard,
    )


@router.callback_query(IsPrivate(), IsAdmin(), PromocodeCallback.filter(F.state == States.DURATION))
async def choose_duration(
    callback: CallbackQuery,
    callback_data: PromocodeCallback,
    promocode: PromocodeService,
) -> None:
    logger.info(
        f"Admin {callback.from_user.id} selected {callback_data.duration} days for promocode."
    )
    promo = await promocode.create_promocode(callback_data.traffic, callback_data.duration)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n"),
        reply_markup=editor_promocodes(),
    )
    await callback.message.answer(text=_("Promocode: {promocode}").format(promocode=promo.code))


# endregion


# region: Delete Promocode
@router.callback_query(F.data == NavigationAction.DELETE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_create_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"Admin {callback.from_user.id} started deleting promocode.")
    await state.set_state(DeletePromocodeStates.waiting_for_promocode)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n" "\n" "_Send promocode to delete_"),
        reply_markup=back_keyboard(NavigationAction.EDITOR_PROMOCODES),
    )


@router.message(DeletePromocodeStates.waiting_for_promocode, IsPrivate(), IsAdmin())
async def handle_promocode_input(
    message: Message, promocode: PromocodeService, state: FSMContext
) -> None:
    code = message.text.strip()
    await message.delete()
    logger.info(f"Admin {message.from_user.id} entered promocode: {code}")

    if await promocode.delete_promocode(code):
        notification = await message.answer(
            text=_("✅ Promocode {} deleted successfully.").format(code)
        )
        message = await state.get_value("message")
        await message.edit_text(
            text=_("🎟️ *Editor promocodes:*"),
            reply_markup=editor_promocodes(),
        )
        await state.clear()
    else:
        notification = await message.answer(
            text=_("❌ Failed to delete promocode. Please try again.")
        )

    await asyncio.sleep(5)
    await notification.delete()


# endregion
