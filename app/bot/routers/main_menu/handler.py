import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY
from app.bot.utils.navigation import NavMain
from app.config import Config
from app.db.models import User, Referral

from .keyboard import main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def is_available_try_for_free(session: AsyncSession, user: User, config: Config) -> bool:
    referral = await Referral.get_referral(session, user.tg_id)
    if not referral:
        return config.shop.TRIAL_ENABLED and not user.is_trial_used

    return not referral.referred_rewarded_at


async def precess_creating_referral(
    session: AsyncSession,
    user: User,
    services: ServicesContainer,
    received_referrer_id: int
) -> bool:
    logger.info(f"Assigning user {user.tg_id} as a referred to a referrer user {received_referrer_id}")
    try:
        referrer = await User.get(session=session, tg_id=received_referrer_id)
        if not referrer or referrer.tg_id == user.tg_id:
            logger.info(f"Failed to assign user {user.tg_id} as a referred to a referrer user {received_referrer_id}."
                        f"Invalid string received.")
            return False

        await Referral.create(
            session=session,
            referrer_tg_id=referrer.tg_id,
            referred_tg_id=user.tg_id
        )
        await services.notification.notify_developer(f"Creating Referral {referrer.tg_id} =>{user.tg_id}")
        logger.info(f"User {user.tg_id} assigned as referred to a referrer with tg id {referrer.tg_id}")
        return True
    except Exception as e:
        logger.critical(f"Error creating Referral to a referred {user.tg_id} (start arg: {received_referrer_id}): {e}")
        return False


@router.message(Command(NavMain.START))
async def command_main_menu(
    message: Message,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    session: AsyncSession,
    command: CommandObject,
    config: Config,
    is_new_user: bool
) -> None:
    logger.info(f"User {user.tg_id} opened main menu page.")
    previous_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)

    if previous_message_id:
        try:
            await message.bot.delete_message(chat_id=user.tg_id, message_id=previous_message_id)
            logger.debug(f"Main message for user {user.tg_id} deleted.")
        except Exception as exception:
            logger.error(f"Failed to delete main message for user {user.tg_id}: {exception}")
        finally:
            await state.clear()

    received_referrer_id = int(command.args) if command.args and command.args.isdigit() else None
    if received_referrer_id and is_new_user:
        await precess_creating_referral(
            session=session,
            user=user,
            services=services,
            received_referrer_id=received_referrer_id
        )

    is_admin = await IsAdmin()(user_id=user.tg_id)
    main_menu = await message.answer(
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(
            is_admin,
            is_available_try_for_free=await is_available_try_for_free(session, user, config)
        ),
    )
    await state.update_data({MAIN_MESSAGE_ID_KEY: main_menu.message_id})


@router.callback_query(F.data == NavMain.MAIN_MENU)
async def callback_main_menu(callback: CallbackQuery, user: User, session: AsyncSession, state: FSMContext, config: Config) -> None:
    logger.info(f"User {user.tg_id} returned to main menu page.")
    await state.clear()
    await state.update_data({MAIN_MESSAGE_ID_KEY: callback.message.message_id})
    is_admin = await IsAdmin()(user_id=user.tg_id)
    await callback.message.edit_text(
        text=_("main_menu:message:main").format(name=user.first_name),
        reply_markup=main_menu_keyboard(
            is_admin,
            is_available_try_for_free=await is_available_try_for_free(session, user, config)
        ),
    )


async def redirect_to_main_menu(
    bot: Bot,
    user: User,
    session: AsyncSession,
    config: Config,
    storage: RedisStorage | None = None,
    state: FSMContext | None = None,
) -> None:
    logger.info(f"User {user.tg_id} redirected to main menu page.")

    if not state:
        state: FSMContext = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id, chat_id=user.tg_id, user_id=user.tg_id),
        )

    main_message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    is_admin = await IsAdmin()(user_id=user.tg_id)

    await bot.edit_message_text(
        text=_("main_menu:message:main").format(name=user.first_name),
        chat_id=user.tg_id,
        message_id=main_message_id,
        reply_markup=main_menu_keyboard(
            is_admin,
            is_available_try_for_free=await is_available_try_for_free(session, user, config),
        ),
    )
