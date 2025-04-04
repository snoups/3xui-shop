import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.models import ServicesContainer
from app.bot.utils.constants import (
    MAIN_MESSAGE_ID_KEY,
    PREVIOUS_CALLBACK_KEY,
    ReferrerRewardLevel,
    ReferrerRewardType,
)
from app.bot.utils.formatting import format_subscription_period
from app.bot.utils.navigation import NavMain, NavReferral
from app.config import Config
from app.db.models import Referral, ReferrerReward, User

from .keyboard import referral_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def generate_referral_summary_text(
    session: AsyncSession,
    user: User,
    config: Config,
    bot_username: str,
) -> str:
    referral_link = f"https://t.me/{bot_username}?start={user.tg_id}"

    text = _("referral:message:user_summary")

    referred_trial_enabled = config.shop.REFERRED_TRIAL_ENABLED
    if referred_trial_enabled:
        referred_duration = format_subscription_period(config.shop.REFERRED_TRIAL_PERIOD)
        text += _("referral:message:user_summary_referred_trial_enabled").format(
            referred_duration=referred_duration,
        )

    referrals_count = await Referral.get_referral_count(session=session, referrer_tg_id=user.tg_id)
    text += _("referral:message:user_summary_invite_link").format(
        referral_link=referral_link,
        referrals_count=referrals_count,
    )

    referrer_reward_enabled = config.shop.REFERRER_REWARD_ENABLED

    if referrer_reward_enabled:
        reward_type = ReferrerRewardType.from_str(config.shop.REFERRER_REWARD_TYPE)
        first_level_rewards_sum = await ReferrerReward.get_rewards_sum(
            session=session,
            tg_id=user.tg_id,
            reward_type=reward_type,
            reward_level=ReferrerRewardLevel.FIRST_LEVEL,
        )
        second_level_rewards_sum = await ReferrerReward.get_rewards_sum(
            session=session,
            tg_id=user.tg_id,
            reward_type=reward_type,
            reward_level=ReferrerRewardLevel.SECOND_LEVEL,
        )

        if reward_type == ReferrerRewardType.DAYS:
            first_referrer_duration = format_subscription_period(
                config.shop.REFERRER_LEVEL_ONE_PERIOD
            )
            second_referrer_duration = format_subscription_period(
                config.shop.REFERRER_LEVEL_TWO_PERIOD
            )
            text += _("referral:message:user_summary_explain_referrer_days").format(
                first_referrer_duration=first_referrer_duration,
                second_referrer_duration=second_referrer_duration,
            )
            first_level_rewards_sum = format_subscription_period(int(first_level_rewards_sum))
            second_level_rewards_sum = format_subscription_period(int(second_level_rewards_sum))
        elif reward_type == ReferrerRewardType.MONEY:
            first_referrer_rate = config.shop.REFERRER_LEVEL_ONE_RATE
            second_referrer_rate = config.shop.REFERRER_LEVEL_TWO_RATE
            text += _("referral:message:user_summary_explain_referrer_money").format(
                first_referrer_rate=first_referrer_rate,
                second_referrer_rate=second_referrer_rate,
            )

            # TODO: handle and format money currencies

        pending_rewards_count = await ReferrerReward.get_pending_rewards_count(
            session=session, user_tg_id=user.tg_id
        )
        text += _("referral:message:user_summary_referrer_rewards").format(
            first_level_rewards_sum=first_level_rewards_sum,
            second_level_rewards_sum=second_level_rewards_sum,
            pending_rewards_count=pending_rewards_count,
        )

    return text


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

    await state.update_data({PREVIOUS_CALLBACK_KEY: NavReferral.MAIN})

    await callback.message.edit_text(
        text=await generate_referral_summary_text(
            session=session,
            user=user,
            config=config,
            bot_username=bot_username,
        ),
        reply_markup=referral_keyboard(),
    )


@router.callback_query(F.data == NavReferral.GET_REFERRED_TRIAL)
async def callback_get_referred_trial(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} triggered getting bonus days.")

    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.show_popup(
            callback=callback,
            text=_("referral:popup:no_available_servers"),
        )
        return

    is_referred_trial_available = await services.referral.is_referred_trial_available(user=user)

    if not is_referred_trial_available:
        await services.notification.show_popup(
            callback=callback,
            text=_("referral:popup:trial_unavailable_for_user"),
        )
        return

    referred_trial_period = config.shop.REFERRED_TRIAL_PERIOD

    success = await services.referral.reward_referred_user(
        user=user, days_count=referred_trial_period
    )

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    if success:
        await state.update_data({PREVIOUS_CALLBACK_KEY: NavMain.MAIN_MENU})
        await callback.bot.edit_message_text(
            text=_("subscription:ntf:trial_activate_success").format(
                duration=format_subscription_period(referred_trial_period),
            ),
            chat_id=callback.message.chat.id,
            message_id=main_message_id,
            reply_markup=referral_keyboard(connect=True),
        )
    else:
        text = _("referral:ntf:referred_trial_activate_failed")
        await services.notification.notify_by_message(
            message=callback.message, text=text, duration=15
        )
