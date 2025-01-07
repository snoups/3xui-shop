import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.keyboards.admin_tools import (
    promocode_duration_keyboard,
    promocode_editor_keyboard,
)
from app.bot.keyboards.back import back_keyboard
from app.bot.navigation import NavAdminTools
from app.bot.services import NotificationService, PlanService, PromocodeService
from app.db.models import Promocode

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class CreatePromocodeStates(StatesGroup):
    """
    States for creating a promocode.
    """

    selecting_duration = State()


class DeletePromocodeStates(StatesGroup):
    """
    States for deleting a promocode.
    """

    promocode_input = State()


class EditPromocodeStates(StatesGroup):
    """
    States for editing a promocode.
    """

    promocode_input = State()
    selecting_duration = State()


@router.callback_query(F.data == NavAdminTools.PROMOCODE_EDITOR, IsPrivate(), IsAdmin())
async def callback_promocode_editor(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for opening the promocode editor.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Admin {callback.from_user.id} opened promocode editor.")
    await state.set_state(None)

    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*"),
        reply_markup=promocode_editor_keyboard(),
    )


# region: Create Promocode
@router.callback_query(F.data == NavAdminTools.CREATE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_create_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting the promocode creation process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} started creating promocode.")
    await state.set_state(CreatePromocodeStates.selecting_duration)
    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*\n" "\n" "_Specify the duration_"),
        reply_markup=promocode_duration_keyboard(),
    )


@router.callback_query(CreatePromocodeStates.selecting_duration, IsPrivate(), IsAdmin())
async def callback_duration_selected(
    callback: CallbackQuery,
    state: FSMContext,
    promocode_service: PromocodeService,
) -> None:
    """
    Handler for selecting the duration for the promocode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        promocode_service (PromocodeService): Service for handling promocode creation.
    """
    logger.info(f"Admin {callback.from_user.id} selected {callback.data} days for promocode.")
    promocode = await promocode_service.create_promocode(int(callback.data))
    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*\n"),
        reply_markup=promocode_editor_keyboard(),
    )
    await NotificationService.notify_by_message(
        message=callback.message,
        text=_("Your created promocode:\n" "```{promocode}```\n" "Duration: {duration}").format(
            promocode=promocode.code,
            duration=PlanService.convert_days_to_period(promocode.duration),
        ),
    )
    await state.set_state(None)


# endregion


# region: Delete Promocode
@router.callback_query(F.data == NavAdminTools.DELETE_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_delete_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting the promocode deletion process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Admin {callback.from_user.id} started deleting promocode.")
    await state.set_state(DeletePromocodeStates.promocode_input)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*\n" "\n" "_Send promocode to delete_"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(DeletePromocodeStates.promocode_input, IsPrivate(), IsAdmin())
async def handle_promocode_input(
    message: Message,
    state: FSMContext,
    promocode_service: PromocodeService,
) -> None:
    """
    Handler for processing the input of a promocode to delete.

    Arguments:
        message (Message): The incoming message containing the promocode to delete.
        state (FSMContext): The state context for managing conversation state.
        promocode_service (PromocodeService): Service for handling promocode deletion.
    """
    input_promocode = message.text.strip()
    logger.info(f"Admin {message.from_user.id} entered promocode: {input_promocode} for deleting.")

    if await promocode_service.delete_promocode(input_promocode):
        message = await state.get_value("message")
        await message.edit_text(
            text=_("🎟️ *Promocode editor:*"),
            reply_markup=promocode_editor_keyboard(),
        )
        await state.set_state(None)
        await NotificationService.notify_by_message(
            message=message,
            text=_("✅ Promocode {promocode} deleted successfully.").format(
                promocode=input_promocode
            ),
            duration=5,
        )
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Failed to delete promocode. Please try again."),
            duration=5,
        )


# endregion


# region Edit Promocode
@router.callback_query(F.data == NavAdminTools.EDIT_PROMOCODE, IsPrivate(), IsAdmin())
async def callback_edit_promocode(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for starting the promocode deletion process.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        state (FSMContext): The state context for managing conversation state.
    """
    logger.info(f"Admin {callback.from_user.id} started deleting promocode.")
    await state.set_state(EditPromocodeStates.promocode_input)
    await state.update_data(message=callback.message)
    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*\n" "\n" "_Send promocode to edit_"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(EditPromocodeStates.promocode_input, IsPrivate(), IsAdmin())
async def handle_promocode_input(
    message: Message,
    state: FSMContext,
    promocode_service: PromocodeService,
) -> None:
    """
    Handler for processing the input of a promocode to delete.

    Arguments:
        message (Message): The incoming message containing the promocode to delete.
        state (FSMContext): The state context for managing conversation state.
        promocode_service (PromocodeService): Service for handling promocode deletion.
    """
    input_promocode = message.text.strip()
    logger.info(f"Admin {message.from_user.id} entered promocode: {input_promocode} for editing.")

    promocode: Promocode = await promocode_service.get_promocode(input_promocode)
    if promocode and not promocode.is_activated:
        await state.set_state(EditPromocodeStates.selecting_duration)
        await state.update_data(input_promocode=input_promocode)
        message = await state.get_value("message")
        await message.edit_text(
            text=_("🎟️ *Promocode editor:*\n" "\n" "_Specify the duration_"),
            reply_markup=promocode_duration_keyboard(),
        )
    else:
        await NotificationService.notify_by_message(
            message=message,
            text=_("❌ Promocode not found or already activated."),
            duration=5,
        )


@router.callback_query(EditPromocodeStates.selecting_duration, IsPrivate(), IsAdmin())
async def callback_duration_selected(
    callback: CallbackQuery,
    state: FSMContext,
    promocode_service: PromocodeService,
) -> None:
    """
    Handler for selecting the duration for the promocode.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
        promocode_service (PromocodeService): Service for handling promocode creation.
    """
    logger.info(f"Admin {callback.from_user.id} selected {callback.data} days for promocode.")
    input_promocode = await state.get_value("input_promocode")
    promocode = await promocode_service.update_promocode(input_promocode, int(callback.data))
    await callback.message.edit_text(
        text=_("🎟️ *Promocode editor:*\n"),
        reply_markup=promocode_editor_keyboard(),
    )
    await NotificationService.notify_by_message(
        message=callback.message,
        text=_("Your edited promocode:\n" "```{promocode}```\n" "New duration: {duration}").format(
            promocode=promocode.code,
            duration=PlanService.convert_days_to_period(promocode.duration),
        ),
    )
    await state.set_state(None)


# endregion
