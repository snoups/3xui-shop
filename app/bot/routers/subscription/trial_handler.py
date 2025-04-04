import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.models import ServicesContainer
from app.bot.routers.subscription.keyboard import trial_success_keyboard
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY, PREVIOUS_CALLBACK_KEY
from app.bot.utils.formatting import format_subscription_period
from app.bot.utils.navigation import NavMain, NavSubscription
from app.config import Config
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavSubscription.GET_TRIAL)
async def callback_get_trial(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} triggered getting non-referral trial period.")
    await state.update_data({PREVIOUS_CALLBACK_KEY: NavMain.MAIN_MENU})

    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.show_popup(
            callback=callback, text=_("subscription:popup:no_available_servers")
        )
        return

    is_trial_available = await services.subscription.is_trial_available(user=user)

    if not is_trial_available:
        await services.notification.show_popup(
            callback=callback, text=_("subscription:popup:trial_unavailable_for_user")
        )
        return
    else:
        trial_period = config.shop.TRIAL_PERIOD
        success = await services.subscription.gift_trial(user=user)

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    if success:
        await callback.bot.edit_message_text(
            text=_("subscription:ntf:trial_activate_success").format(
                duration=format_subscription_period(trial_period),
            ),
            chat_id=callback.message.chat.id,
            message_id=main_message_id,
            reply_markup=trial_success_keyboard(),
        )
    else:
        text = _("subscription:popup:trial_activate_failed")
        await services.notification.show_popup(callback=callback, text=text)
