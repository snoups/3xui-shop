import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.utils.constants import INPUT_PROMOCODE_KEY, MAIN_MESSAGE_ID_KEY
from app.bot.utils.formatting import format_subscription_period
from app.bot.utils.navigation import NavAdminTools
from app.db.models import Promocode, User

from .keyboard import promocode_duration_keyboard, promocode_editor_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class CreatePromocodeStates(StatesGroup):
    selecting_duration = State()


class DeletePromocodeStates(StatesGroup):
    promocode_input = State()


class EditPromocodeStates(StatesGroup):
    promocode_input = State()
    selecting_duration = State()


async def show_promocode_editor_main(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    await message.bot.edit_message_text(
        text=_("promocode_editor:message:main"),
        chat_id=message.chat.id,
        message_id=main_message_id,
        reply_markup=promocode_editor_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.PROMOCODE_EDITOR, IsAdmin())
async def callback_promocode_editor(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} opened promocode editor.")
    await show_promocode_editor_main(message=callback.message, state=state)


# region: Create Promocode
@router.callback_query(F.data == NavAdminTools.CREATE_PROMOCODE, IsAdmin())
async def callback_create_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started creating promocode.")
    await state.set_state(CreatePromocodeStates.selecting_duration)
    await callback.message.edit_text(
        text=_("promocode_editor:message:create"),
        reply_markup=promocode_duration_keyboard(),
    )


@router.callback_query(CreatePromocodeStates.selecting_duration, IsAdmin())
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} selected {callback.data} days for promocode.")
    promocode = await Promocode.create(session=session, duration=int(callback.data))
    await show_promocode_editor_main(message=callback.message, state=state)

    if promocode:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("promocode_editor:ntf:created_success").format(
                promocode=promocode.code,
                duration=format_subscription_period(promocode.duration),
            ),
        )
    else:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("promocode_editor:ntf:create_failed"),
            duration=5,
        )


# endregion


# region: Delete Promocode
@router.callback_query(F.data == NavAdminTools.DELETE_PROMOCODE, IsAdmin())
async def callback_delete_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started deleting promocode.")
    await state.set_state(DeletePromocodeStates.promocode_input)
    await callback.message.edit_text(
        text=_("promocode_editor:message:delete"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(DeletePromocodeStates.promocode_input, IsAdmin())
async def handle_promocode_input(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    input_promocode = message.text.strip()
    logger.info(f"Admin {user.tg_id} entered promocode: {input_promocode} for deleting.")

    if await Promocode.delete(session=session, code=input_promocode):
        await show_promocode_editor_main(message=message, state=state)
        await services.notification.notify_by_message(
            message=message,
            text=_("promocode_editor:ntf:deleted_success").format(promocode=input_promocode),
            duration=5,
        )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("promocode_editor:ntf:delete_failed"),
            duration=5,
        )


# endregion


# region Edit Promocode
@router.callback_query(F.data == NavAdminTools.EDIT_PROMOCODE, IsAdmin())
async def callback_edit_promocode(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} started deleting promocode.")
    await state.set_state(EditPromocodeStates.promocode_input)
    await callback.message.edit_text(
        text=_("promocode_editor:message:edit"),
        reply_markup=back_keyboard(NavAdminTools.PROMOCODE_EDITOR),
    )


@router.message(EditPromocodeStates.promocode_input, IsAdmin())
async def handle_promocode_input(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    input_promocode = message.text.strip()
    logger.info(f"Admin {user.tg_id} entered promocode: {input_promocode} for editing.")

    promocode = await Promocode.get(session=session, code=input_promocode)
    if promocode and not promocode.is_activated:
        await state.set_state(EditPromocodeStates.selecting_duration)
        await state.update_data({INPUT_PROMOCODE_KEY: input_promocode})
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await message.bot.edit_message_text(
            text=_("promocode_editor:message:edit_duration").format(
                promocode=promocode.code,
                duration=promocode.duration,
            ),
            chat_id=message.chat.id,
            message_id=main_message_id,
            reply_markup=promocode_duration_keyboard(),
        )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("promocode_editor:ntf:edit_failed"),
            duration=5,
        )


@router.callback_query(EditPromocodeStates.selecting_duration, IsAdmin())
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} selected {callback.data} days for promocode.")
    input_promocode = await state.get_value(INPUT_PROMOCODE_KEY)
    promocode = await Promocode.update(
        session=session,
        code=input_promocode,
        duration=int(callback.data),
    )
    await show_promocode_editor_main(message=callback.message, state=state)
    await services.notification.notify_by_message(
        message=callback.message,
        text=_("promocode_editor:ntf:edited_success").format(
            promocode=promocode.code,
            duration=format_subscription_period(promocode.duration),
        ),
    )


# endregion
