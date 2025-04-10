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
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY, Currency
from app.bot.utils.navigation import NavAdminTools
from app.db.models.invite import Invite
from app.db.models.user import User

from .keyboard import (invite_details_keyboard, invite_editor_keyboard,
                       invite_list_keyboard)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class CreateInviteStates(StatesGroup):
    invite_input = State()


@router.callback_query(F.data == NavAdminTools.INVITE_EDITOR, IsAdmin())
async def callback_invite_editor(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    logger.info(f"Admin {user.tg_id} opened invite editor.")
    await callback.message.edit_text(
        text=_("invite_editor:message:main"),
        reply_markup=invite_editor_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.CREATE_INVITE, IsAdmin())
async def callback_create_invite(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    logger.info(f"Admin {user.tg_id} started creating invite link.")
    await state.set_state(CreateInviteStates.invite_input)
    await state.update_data({MAIN_MESSAGE_ID_KEY: callback.message.message_id})

    await callback.message.edit_text(
        text=_("invite_editor:message:enter_name"),
        reply_markup=back_keyboard(NavAdminTools.INVITE_EDITOR),
    )


@router.message(CreateInviteStates.invite_input, IsAdmin())
async def handle_invite_input(
    message: Message,
    user: User,
    session: AsyncSession,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    invite_name = message.text.strip()
    logger.info(f"Admin {user.tg_id} entered invite name: {invite_name}")

    data = await state.get_data()
    main_message_id = data.get(MAIN_MESSAGE_ID_KEY)

    try:
        invite = await Invite.create(session=session, name=invite_name)
        bot_username = (await message.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start={invite.hash_code}"

        await state.clear()

        await message.bot.edit_message_text(
            text=_("invite_editor:message:created_success").format(
                name=invite_name, link=invite_link
            ),
            chat_id=message.chat.id,
            message_id=main_message_id,
            reply_markup=back_keyboard(NavAdminTools.INVITE_EDITOR),
        )
    except Exception as e:
        logger.error(f"Error creating invite: {e}")
        await services.notification.notify_by_message(
            message=message,
            text=_("invite_editor:ntf:create_failed"),
            duration=5,
        )


@router.callback_query(F.data == NavAdminTools.LIST_INVITES, IsAdmin())
async def callback_list_invites(
    callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext
) -> None:
    logger.info(f"Admin {user.tg_id} is listing invites.")

    invites = await Invite.get_all(session=session)

    if invites:
        await callback.message.edit_text(
            text=_("invite_editor:message:list"),
            reply_markup=invite_list_keyboard(invites),
        )
    else:
        await callback.message.edit_text(
            text=_("invite_editor:message:no_invites"),
            reply_markup=back_keyboard(NavAdminTools.INVITE_EDITOR),
        )


@router.callback_query(F.data.startswith(f"{NavAdminTools.SHOW_INVITE_PAGE}:"), IsAdmin())
async def callback_invite_page(
    callback: CallbackQuery, user: User, session: AsyncSession
) -> None:
    page = int(callback.data.split(":")[1])
    invites = await Invite.get_all(session=session)

    logger.info(f"Admin {user.tg_id} is now on page #{page + 1} of invites.")

    await callback.message.edit_text(
        text=_("invite_editor:message:list"),
        reply_markup=invite_list_keyboard(invites, page=page),
    )


@router.callback_query(F.data.startswith(f"{NavAdminTools.SHOW_INVITE_DETAILS}:"), IsAdmin())
async def callback_invite_details(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
) -> None:
    invite_id = int(callback.data.split(":")[1])
    invite = await session.get(Invite, invite_id)

    logger.info(f"Admin {user.tg_id} is checking invite {invite.name}.")

    if invite:
        bot_username = (await callback.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start={invite.hash_code}"

        status = (
            _("invite_editor:status:active")
            if invite.is_active
            else _("invite_editor:status:inactive")
        )

        stats = await services.invite_stats.get_detailed_stats(invite.name, session)

        revenue_text = "\n\n" + "* " + _("invite_editor:revenue:title")
        if stats["revenue"] and len(stats["revenue"]) > 0:
            for currency, amount in stats["revenue"].items():
                currency_symbol = Currency.from_code(currency).symbol
                revenue_text += f"\n* {amount:.2f} {currency_symbol}"
        else:
            revenue_text += " " + _("invite_editor:revenue:none")

        users_stats_text = "\n\n* " + _(
            "invite_editor:statistics:users_count"
        ).format(count=stats["users_count"])
        users_stats_text += "\n* " + _(
            "invite_editor:statistics:trial_users_count"
        ).format(count=stats["trial_users_count"])
        users_stats_text += "\n* " + _(
            "invite_editor:statistics:paid_users_count"
        ).format(count=stats["paid_users_count"])
        users_stats_text += "\n* " + _(
            "invite_editor:statistics:repeat_customers_count"
        ).format(count=stats["repeat_customers_count"])

        await callback.message.edit_text(
            text=_("invite_editor:message:details").format(
                name=invite.name,
                link=invite_link,
                clicks=invite.clicks,
                created_at=invite.created_at.strftime("%Y-%m-%d %H:%M"),
                status=status,
            )
            + revenue_text
            + users_stats_text,
            reply_markup=invite_details_keyboard(invite),
        )


@router.callback_query(F.data.startswith(f"{NavAdminTools.TOGGLE_INVITE_STATUS}:"), IsAdmin())
async def callback_toggle_invite(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
) -> None:
    invite_id = int(callback.data.split(":")[1])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await callback.answer(_("invite_editor:ntf:not_found"), show_alert=True)
        return

    invite.is_active = not invite.is_active
    await session.commit()

    logger.info(
        f"Admin {user.tg_id} has changed invite {invite.name} status to {bool(invite.is_active)}."
    )

    status = (
        _("invite_editor:status:active")
        if invite.is_active
        else _("invite_editor:status:inactive")
    )
    await callback.answer(
        _("invite_editor:ntf:status_changed").format(status=status), show_alert=True
    )

    await callback_invite_details(
        callback=callback,
        user=user,
        session=session,
        services=services,
    )


@router.callback_query(F.data.startswith(f"{NavAdminTools.DELETE_INVITE_CONFIRM}:"), IsAdmin())
async def callback_delete_invite(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
) -> None:
    invite_id = int(callback.data.split(":")[1])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await callback.answer(_("invite_editor:ntf:not_found"), show_alert=True)
        return

    invite_name = invite.name

    logger.info(f"Admin {user.tg_id} has deleted invite {invite_name}.")

    await session.delete(invite)
    await session.commit()

    await callback.answer(
        _("invite_editor:ntf:deleted").format(name=invite_name), show_alert=True
    )

    await callback_list_invites(
        callback=callback,
        user=user,
        session=session,
        state=None,
    )
