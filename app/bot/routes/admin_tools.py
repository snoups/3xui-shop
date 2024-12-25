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
)
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import CreatePromocodeCallback, Navigation
from app.bot.services.promocode import PromocodeService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class DeletePromocodeStates(StatesGroup):
    """
    States for deleting a promocode.
    """

    waiting_for_promocode = State()


@router.callback_query(F.data == Navigation.ADMIN_TOOLS, IsPrivate(), IsAdmin())
async def callback_admin_tools(callback: CallbackQuery) -> None:
    """
    Handler for opening the admin tools menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened admin tools.")
    await callback.message.edit_text(
        text=_("🛠 *Admin tools:*"),
        reply_markup=admin_tools_keyboard(),
    )


@router.callback_query(F.data == Navigation.STATISTICS, IsPrivate(), IsAdmin())
async def callback_statistics(callback: CallbackQuery) -> None:
    """
    Handler for opening the statistics menu.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened statistics.")
    pass


@router.callback_query(F.data == Navigation.EDITOR_USERS, IsPrivate(), IsAdmin())
async def callback_editor_users(callback: CallbackQuery) -> None:
    """
    Handler for opening the user editor.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened editor users.")
    pass


@router.callback_query(F.data == Navigation.EDITOR_PROMOCODES, IsPrivate(), IsAdmin())
async def callback_editor_promocodes(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for opening the promocode editor.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Admin {callback.from_user.id} opened editor promocodes.")
    await state.clear()
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*"),
        reply_markup=editor_promocodes(),
    )


@router.callback_query(F.data == Navigation.SEND_NOTIFICATION, IsPrivate(), IsAdmin())
async def callback_send_notification(callback: CallbackQuery) -> None:
    """
    Handler for sending notifications.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} opened send notification.")
    pass


@router.callback_query(F.data == Navigation.CREATE_BACKUP, IsPrivate(), IsAdmin())
async def callback_create_backup(callback: CallbackQuery) -> None:
    """
    Handler for creating backups.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} created backup.")
    pass


@router.callback_query(F.data == Navigation.RESTART_BOT, IsPrivate(), IsAdmin())
async def callback_restart_bot(callback: CallbackQuery) -> None:
    """
    Handler for restarting the bot.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} restarted bot.")
    pass


# region: Create Promocode
@router.callback_query(F.data == Navigation.CREATE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_create_promocode(callback: CallbackQuery) -> None:
    """
    Handler for starting the promocode creation process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} started creating promocode.")
    callback_data = CreatePromocodeCallback(state=Navigation.DURATION)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n" "\n" "_Specify the duration_"),
        reply_markup=promocode_duration_keyboard(callback_data),
    )


@router.callback_query(
    CreatePromocodeCallback.filter(F.state == Navigation.DURATION), IsPrivate(), IsAdmin()
)
async def callback_duration_selected(
    callback: CallbackQuery,
    callback_data: CreatePromocodeCallback,
    promocode_service: PromocodeService,
) -> None:
    """
    Handler for selecting the duration for the promocode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        callback_data (CreatePromocodeCallback): The callback data containing state info.
        promocode_service (PromocodeService): Service for handling promocode creation.
    """
    logger.info(
        f"Admin {callback.from_user.id} selected {callback_data.duration} days for promocode."
    )
    promocode = await promocode_service.create_promocode(callback_data.duration)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n"),
        reply_markup=editor_promocodes(),
    )
    await callback.message.answer(
        text=_("Your created promocode: ```{promocode}```").format(promocode=promocode.code)
    )


# endregion


# region: Delete Promocode
@router.callback_query(F.data == Navigation.DELETE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_delete_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting the promocode deletion process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Admin {callback.from_user.id} started deleting promocode.")
    await state.set_state(DeletePromocodeStates.waiting_for_promocode)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Editor promocodes:*\n" "\n" "_Send promocode to delete_"),
        reply_markup=back_keyboard(Navigation.EDITOR_PROMOCODES),
    )


@router.message(DeletePromocodeStates.waiting_for_promocode, IsPrivate(), IsAdmin())
async def handle_promocode_input(
    message: Message, promocode_service: PromocodeService, state: FSMContext
) -> None:
    """
    Handler for processing the input of a promocode to delete.

    Arguments:
        message (Message): The incoming message containing the promocode to delete.
        promocode_service (PromocodeService): Service for handling promocode deletion.
        state (FSMContext): The state context for managing conversation state.
    """
    input_promocode = message.text.strip()
    await message.delete()
    logger.info(f"Admin {message.from_user.id} entered promocode: {input_promocode} for deleting.")

    if await promocode_service.delete_promocode(input_promocode):
        notification = await message.answer(
            text=_("✅ Promocode {promocode} deleted successfully.").format(
                promocode=input_promocode
            )
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
