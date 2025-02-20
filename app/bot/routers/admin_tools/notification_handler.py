import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.routers.misc.keyboard import back_keyboard, close_notification_keyboard
from app.bot.utils.constants import (
    MAIN_MESSAGE_ID_KEY,
    NOTIFICATION_CHAT_IDS_KEY,
    NOTIFICATION_LAST_MESSAGE_IDS_KEY,
    NOTIFICATION_MESSAGE_TEXT_KEY,
    NOTIFICATION_PRE_MESSAGE_TEXT_KEY,
)
from app.bot.utils.navigation import NavAdminTools
from app.bot.utils.validation import is_valid_message_text, is_valid_user_id
from app.db.models import User

from .keyboard import (
    confirm_send_notification_keyboard,
    last_notification_keyboard,
    notification_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class NotificationStates(StatesGroup):
    user_id = State()
    message_to_user = State()
    message_to_all = State()
    message_edit = State()


async def show_notification_main(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    await message.bot.edit_message_text(
        text=_("notification:message:main"),
        chat_id=message.chat.id,
        message_id=main_message_id,
        reply_markup=notification_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.NOTIFICATION, IsAdmin())
async def callback_send_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    logger.info(f"Admin {user.tg_id} opened send notification.")
    await show_notification_main(message=callback.message, state=state)


@router.callback_query(F.data == NavAdminTools.SEND_NOTIFICATION_USER, IsAdmin())
async def callback_send_notification_user(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    logger.info(f"Admin {user.tg_id} opened send notification to user.")
    await callback.message.edit_text(
        text=_("notification:message:send_to_user"),
        reply_markup=back_keyboard(NavAdminTools.NOTIFICATION),
    )
    await state.set_state(NotificationStates.user_id)


@router.message(NotificationStates.user_id)
async def message_user_id(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    if message.forward_from:
        user_id = str(message.forward_from.id)
    else:
        user_id = message.text.strip()
    logger.info(f"Admin {user.tg_id} sent user id {user_id} for notification.")

    if is_valid_user_id(user_id):
        user = await User.get(session=session, tg_id=user_id)

        if user:
            await state.update_data({NOTIFICATION_CHAT_IDS_KEY: [user_id]})
            main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
            await state.set_state(NotificationStates.message_to_user)
            await message.bot.edit_message_text(
                text=_("notification:message:send_message_for_user").format(
                    user_id=user_id,
                    first_name=user.first_name,
                ),
                chat_id=message.chat.id,
                message_id=main_message_id,
                reply_markup=back_keyboard(NavAdminTools.NOTIFICATION),
            )
        else:
            await services.notification.notify_by_message(
                message=message,
                text=_("notification:ntf:user_not_found"),
                duration=5,
            )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("notification:ntf:invalid_user_id"),
            duration=5,
        )


@router.message(NotificationStates.message_to_user)
async def message_to_user(
    message: Message,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    text = message.text.strip()
    user_ids = await state.get_value(NOTIFICATION_CHAT_IDS_KEY)
    user_id = user_ids[0]
    logger.info(f"Admin {user.tg_id} sent message for user {user_id}.")

    if is_valid_message_text(text):
        await state.update_data({NOTIFICATION_PRE_MESSAGE_TEXT_KEY: text})
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await message.bot.edit_message_text(
            text=_("notification:message:confirm_send_notification").format(text=text),
            chat_id=message.chat.id,
            message_id=main_message_id,
            reply_markup=confirm_send_notification_keyboard(),
        )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )


@router.callback_query(
    F.data == NavAdminTools.CONFIRM_SEND_NOTIFICATION,
    NotificationStates.message_to_user,
    IsAdmin(),
)
async def callback_confirm_send_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} confirmed send notification.")
    text = await state.get_value(NOTIFICATION_PRE_MESSAGE_TEXT_KEY)

    if not is_valid_message_text(text):
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )
        return None

    user_id = await state.get_value(NOTIFICATION_CHAT_IDS_KEY)
    notification = await services.notification.notify_by_id(chat_id=user_id[0], text=text)

    if notification:
        await state.update_data({NOTIFICATION_LAST_MESSAGE_IDS_KEY: [notification.message_id]})
        await state.update_data({NOTIFICATION_MESSAGE_TEXT_KEY: text})
        await show_notification_main(message=callback.message, state=state)
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:sent_success"),
            duration=5,
        )
    else:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:failed_to_send_message"),
            duration=5,
        )


@router.callback_query(F.data == NavAdminTools.SEND_NOTIFICATION_ALL, IsAdmin())
async def callback_send_notification_all(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    logger.info(f"Admin {user.tg_id} opened send notification to all.")
    await callback.message.edit_text(
        text=_("notification:message:send_to_all"),
        reply_markup=back_keyboard(NavAdminTools.NOTIFICATION),
    )
    await state.set_state(NotificationStates.message_to_all)


@router.message(NotificationStates.message_to_all)
async def message_to_all(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    text = message.text.strip()
    logger.info(f"Admin {user.tg_id} sent message for all.")

    if is_valid_message_text(text):
        await state.update_data({NOTIFICATION_PRE_MESSAGE_TEXT_KEY: text})
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await message.bot.edit_message_text(
            text=_("notification:message:confirm_send_notification").format(text=text),
            chat_id=message.chat.id,
            message_id=main_message_id,
            reply_markup=confirm_send_notification_keyboard(),
        )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )


@router.callback_query(
    F.data == NavAdminTools.CONFIRM_SEND_NOTIFICATION,
    NotificationStates.message_to_all,
    IsAdmin(),
)
async def callback_confirm_send_notification_all(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} confirmed send notification to all.")
    text = await state.get_value(NOTIFICATION_PRE_MESSAGE_TEXT_KEY)

    if not is_valid_message_text(text):
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )
        return None

    await state.update_data({NOTIFICATION_MESSAGE_TEXT_KEY: text})
    users = await User.get_all(session=session)
    await services.notification.notify_by_message(
        message=callback.message,
        text=_("notification:ntf:sending_to_all").format(
            count=len(users),
        ),
        duration=5,
    )
    user_ids = []
    message_ids = []

    for _user in users:
        notification = await services.notification.notify_by_id(chat_id=_user.tg_id, text=text)

        if notification:
            user_ids.append(_user.tg_id)
            message_ids.append(notification.message_id)

    await state.update_data({NOTIFICATION_CHAT_IDS_KEY: user_ids})
    await state.update_data({NOTIFICATION_LAST_MESSAGE_IDS_KEY: message_ids})
    await show_notification_main(message=callback.message, state=state)
    await services.notification.notify_by_message(
        message=callback.message,
        text=_("notification:ntf:sent_success_all").format(
            success=len(user_ids),
            failed=len(users) - len(user_ids),
        ),
        duration=5,
    )


@router.callback_query(F.data == NavAdminTools.LAST_NOTIFICATION, IsAdmin())
async def callback_last_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} opened last notification.")
    user_ids = await state.get_value(NOTIFICATION_CHAT_IDS_KEY)
    message_text = await state.get_value(NOTIFICATION_MESSAGE_TEXT_KEY)
    if user_ids and len(user_ids) > 0:
        await callback.message.edit_text(
            text=_("notification:message:last_notification").format(
                message_count=len(user_ids),
                message_text=message_text,
            ),
            reply_markup=last_notification_keyboard(),
        )
    else:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:last_notification_not_found"),
            duration=5,
        )


@router.callback_query(F.data == NavAdminTools.EDIT_NOTIFICATION, IsAdmin())
async def callback_edit_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
) -> None:
    logger.info(f"Admin {user.tg_id} opened edit notification.")
    await callback.message.edit_text(
        text=_("notification:message:edit_notification"),
        reply_markup=back_keyboard(NavAdminTools.LAST_NOTIFICATION),
    )
    await state.set_state(NotificationStates.message_edit)


@router.message(NotificationStates.message_edit)
async def message_edit(
    message: Message,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    text = message.text.strip()
    logger.info(f"Admin {user.tg_id} edit notification.")

    if is_valid_message_text(text):
        await state.update_data({NOTIFICATION_PRE_MESSAGE_TEXT_KEY: text})
        main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
        await message.bot.edit_message_text(
            text=_("notification:message:confirm_send_notification").format(text=text),
            chat_id=message.chat.id,
            message_id=main_message_id,
            reply_markup=confirm_send_notification_keyboard(),
        )
    else:
        await services.notification.notify_by_message(
            message=message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )


@router.callback_query(
    F.data == NavAdminTools.CONFIRM_SEND_NOTIFICATION,
    NotificationStates.message_edit,
    IsAdmin(),
)
async def callback_confirm_edit_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} confirmed edit notification.")
    text = await state.get_value(NOTIFICATION_PRE_MESSAGE_TEXT_KEY)
    chat_ids = await state.get_value(NOTIFICATION_CHAT_IDS_KEY)
    last_message_ids = await state.get_value(NOTIFICATION_LAST_MESSAGE_IDS_KEY)
    chat_ids_count = len(chat_ids)

    if not is_valid_message_text(text):
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:invalid_message_text"),
            duration=5,
        )
        return None

    await state.update_data({NOTIFICATION_MESSAGE_TEXT_KEY: text})

    if chat_ids and last_message_ids and chat_ids_count > 0:
        if chat_ids_count > 1:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:editing_notification").format(
                    count=chat_ids_count,
                ),
                duration=5,
            )
        success = 0
        edited = False
        for chat_id, last_message_id in zip(chat_ids, last_message_ids):

            try:
                edited = await callback.message.bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=last_message_id,
                    reply_markup=close_notification_keyboard(),
                )

                if edited:
                    success += 1
            except Exception as exception:
                logger.error(
                    f"Error editing message {last_message_id} from chat {chat_id}: {exception}"
                )
                chat_ids.remove(chat_id)
                last_message_ids.remove(last_message_id)

        await state.update_data({NOTIFICATION_CHAT_IDS_KEY: chat_ids})
        await state.update_data({NOTIFICATION_LAST_MESSAGE_IDS_KEY: last_message_ids})

        await show_notification_main(message=callback.message, state=state)

        if not edited:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:edited_failed"),
                duration=5,
            )
            return None

        if chat_ids_count > 1:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:edited_success_all").format(
                    success=success,
                    failed=chat_ids_count - success,
                ),
                duration=5,
            )
        else:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:edited_success"),
                duration=5,
            )
    else:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:no_messages_to_edit"),
            duration=5,
        )


@router.callback_query(F.data == NavAdminTools.DELETE_NOTIFICATION, IsAdmin())
async def callback_delete_notification(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} delete notification.")
    chat_ids = await state.get_value(NOTIFICATION_CHAT_IDS_KEY)
    last_message_ids = await state.get_value(NOTIFICATION_LAST_MESSAGE_IDS_KEY)
    chat_ids_count = len(chat_ids)

    if last_message_ids and chat_ids and chat_ids_count > 0:
        for chat_id, last_message_id in zip(chat_ids, last_message_ids):
            deleted = False
            success = 0

            try:
                deleted = await callback.message.bot.delete_message(
                    chat_id=chat_id,
                    message_id=last_message_id,
                )
                if deleted:
                    success += 1
            except Exception as exception:
                logger.error(
                    f"Error deleting message {last_message_id} from chat {chat_id}: {exception}"
                )

        await state.update_data({NOTIFICATION_CHAT_IDS_KEY: None})
        await state.update_data({NOTIFICATION_LAST_MESSAGE_IDS_KEY: None})
        await state.update_data({NOTIFICATION_MESSAGE_TEXT_KEY: None})
        await show_notification_main(message=callback.message, state=state)

        if not deleted:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:deleted_failed"),
                duration=5,
            )
            return None

        if chat_ids_count > 1:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:deleted_success_all").format(
                    success=success,
                    failed=chat_ids_count - success,
                ),
                duration=5,
            )
        else:
            await services.notification.notify_by_message(
                message=callback.message,
                text=_("notification:ntf:deleted_success"),
                duration=5,
            )
    else:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("notification:ntf:deleted_failed"),
            duration=5,
        )
