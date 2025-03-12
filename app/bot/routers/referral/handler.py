import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.models import ServicesContainer
from app.bot.utils.constants import PREVIOUS_CALLBACK_KEY
from app.bot.utils.navigation import NavReferral
from app.config import Config
from app.db.models import User, Referral
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY

from .keyboard import referral_keyboard
from app.bot.utils.formatting import format_subscription_period

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavReferral.MAIN)
async def callback_referral(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    session: AsyncSession,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} opened referral page.")

    bot_username = (await callback.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={callback.from_user.id}"

    await state.update_data({PREVIOUS_CALLBACK_KEY: NavReferral.MAIN})

    referrals_count = await Referral.count_referrals(session=session, referrer_tg_id=user.tg_id)

    duration = format_subscription_period(config.shop.REFERRAL_PERIOD)

    reply_markup = referral_keyboard()
    await callback.message.edit_text(
        text=_("referral:message:user_summary").format(
            duration=duration,
            referral_link=referral_link,
            referrals_count=referrals_count
        ),
        reply_markup=reply_markup,
    )


@router.callback_query(F.data == NavReferral.GET_BONUS_DAYS)
async def callback_get_bonus_days(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    session: AsyncSession,
    services: ServicesContainer,
    config: Config
) -> None:
    logger.info(f"User {user.tg_id} triggered getting bonus days.")

    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.notify_by_message(
            message=callback.message,
            text=_("referral:ntf:no_available_servers"),
            duration=5,
        )
        return

    referral = await Referral.get_referral(session, user.tg_id)
    is_trial_available = not referral and config.shop.TRIAL_ENABLED and not user.is_trial_used
    is_referrer_reward_available = referral and not referral.referred_rewarded_at

    if not is_trial_available and not is_referrer_reward_available:
        await callback.answer(text=_("referral:popup:bonus_days_unavailable_for_user"), show_alert=True)
        return

    if is_trial_available:
        bonus_days = config.shop.TRIAL_PERIOD
    else:
        bonus_days = config.shop.REFERRAL_PERIOD

    if is_trial_available:
        success = await services.vpn.gift_trial(user=user)
    else:
        success = await services.vpn.reward_referral(referred_tg_id=user.tg_id)

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    if success:
        await callback.bot.edit_message_text(
            text=_("referral:ntf:bonus_days_activate_success").format(
                duration=format_subscription_period(bonus_days),
            ),
            chat_id=callback.message.chat.id,
            message_id=main_message_id,
            reply_markup=referral_keyboard(),
        )
    else:
        text = _("referral:ntf:bonus_days_activate_failed")
        await services.notification.notify_by_message(message=callback.message, text=text, duration=15)
