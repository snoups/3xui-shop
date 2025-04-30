import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.payment_gateways import GatewayFactory
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY, Currency
from app.bot.utils.navigation import NavAdminTools
from app.db.models import Invite, User

from .keyboard import (
    confirm_delete_invite_keyboard,
    invite_details_keyboard,
    invite_editor_keyboard,
    invite_list_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class CreateInviteStates(StatesGroup):
    invite_input = State()


@router.callback_query(F.data == NavAdminTools.INVITE_EDITOR, IsAdmin())
async def callback_invite_editor(callback: CallbackQuery, user: User, state: FSMContext) -> None:
    logger.info(f"Admin {user.tg_id} opened invite editor.")
    await state.set_state(None)
    await callback.message.edit_text(
        text=_("invite_editor:message:main"),
        reply_markup=invite_editor_keyboard(),
    )


@router.callback_query(F.data == NavAdminTools.CREATE_INVITE, IsAdmin())
async def callback_create_invite(callback: CallbackQuery, user: User, state: FSMContext) -> None:
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

        await state.set_state(None)

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


@router.callback_query(F.data.startswith(NavAdminTools.SHOW_INVITE_PAGE), IsAdmin())
async def callback_invite_page(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    page = int(callback.data.split("_")[3])
    invites = await Invite.get_all(session=session)

    logger.info(f"Admin {user.tg_id} is now on page #{page + 1} of invites.")

    await callback.message.edit_text(
        text=_("invite_editor:message:list"),
        reply_markup=invite_list_keyboard(invites, page=page),
    )


@router.callback_query(F.data.startswith(NavAdminTools.SHOW_INVITE_DETAILS), IsAdmin())
async def callback_invite_details(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
    gateway_factory: GatewayFactory,
) -> None:
    invite_id = int(callback.data.split("_")[3])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await services.notification.show_popup(
            callback=callback,
            text=_("invite_editor:popup:not_found"),
        )
        return

    logger.info(f"Admin {user.tg_id} is checking invite {invite.name}.")

    bot_username = (await callback.bot.get_me()).username
    invite_link = f"https://t.me/{bot_username}?start={invite.hash_code}"

    status = (
        _("invite_editor:status:active") if invite.is_active else _("invite_editor:status:inactive")
    )

    payment_method_currencies = {}
    for gateway in gateway_factory.get_gateways():
        payment_method_currencies[gateway.callback] = gateway.currency.code

    try:
        stats = await services.invite_stats.get_detailed_stats(
            invite_name=invite.name,
            session=session,
            payment_method_currencies=payment_method_currencies,
        )
    except Exception as e:
        logger.error(f"Failed to get invite stats for {invite.name}: {e}")
        await services.notification.show_popup(
            callback=callback,
            text=_("invite_editor:popup:failed_get_stats"),
        )
        return

    if stats.revenue and len(stats.revenue) > 0:
        revenue_lines = []
        for currency, amount in stats.revenue.items():
            currency_symbol = Currency.from_code(currency).symbol
            revenue_lines.append(f"• {amount:.2f} {currency_symbol}")
        revenue_text = "\n".join(revenue_lines)
    else:
        revenue_text = "• " + _("invite_editor:revenue:none")

    await callback.message.edit_text(
        text=_("invite_editor:message:details").format(
            name=invite.name,
            link=invite_link,
            clicks=invite.clicks,
            created_at=invite.created_at.strftime("%Y-%m-%d %H:%M"),
            status=status,
            revenue_text=revenue_text,
            users_count=stats.users_count,
            trial_users_count=stats.trial_users_count,
            paid_users_count=stats.paid_users_count,
            repeat_customers_count=stats.repeat_customers_count,
        ),
        reply_markup=invite_details_keyboard(invite),
    )


@router.callback_query(F.data.startswith(NavAdminTools.TOGGLE_INVITE_STATUS), IsAdmin())
async def callback_toggle_invite(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
    gateway_factory: GatewayFactory,
) -> None:
    invite_id = int(callback.data.split("_")[3])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await services.notification.show_popup(
            callback=callback,
            text=_("invite_editor:popup:not_found"),
        )
        return

    invite.is_active = not invite.is_active
    await session.commit()

    logger.info(
        f"Admin {user.tg_id} has changed invite {invite.name} status to {bool(invite.is_active)}."
    )

    status = (
        _("invite_editor:status:active") if invite.is_active else _("invite_editor:status:inactive")
    )

    await services.notification.show_popup(
        callback=callback,
        text=_("invite_editor:popup:status_changed").format(status=status),
    )

    await callback_invite_details(
        callback=callback,
        user=user,
        session=session,
        services=services,
        gateway_factory=gateway_factory,
    )


@router.callback_query(F.data.startswith(NavAdminTools.CONFIRM_DELETE_INVITE), IsAdmin())
async def callback_delete_invite_prompt(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
) -> None:
    invite_id = int(callback.data.split("_")[3])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await services.notification.show_popup(
            callback=callback,
            text=_("invite_editor:popup:not_found"),
        )
        return

    invite_name = invite.name

    logger.info(f"Admin {user.tg_id} confirmed deletion of invite {invite_name}.")

    await callback.message.edit_text(
        text=_("invite_editor:message:confirm_delete").format(name=invite.name),
        reply_markup=confirm_delete_invite_keyboard(invite_id),
    )


@router.callback_query(F.data.startswith(NavAdminTools.DELETE_INVITE), IsAdmin())
async def callback_delete_invite(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    services: ServicesContainer,
) -> None:
    invite_id = int(callback.data.split("_")[2])
    invite = await session.get(Invite, invite_id)

    if not invite:
        await services.notification.show_popup(
            callback=callback,
            text=_("invite_editor:popup:not_found"),
        )
        return

    invite_name = invite.name

    logger.info(f"Admin {user.tg_id} has deleted invite {invite_name}.")

    await session.delete(invite)
    await session.commit()

    await services.notification.show_popup(
        callback=callback,
        text=_("invite_editor:popup:deleted").format(name=invite_name),
    )

    await callback_list_invites(
        callback=callback,
        user=user,
        session=session,
        state=None,
    )
