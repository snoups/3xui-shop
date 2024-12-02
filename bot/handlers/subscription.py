from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.subscription_keyboard import get_subscription_keyboard
from bot.utils.localization import localization
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
router = Router(name=__name__)


@router.message(Command("subscription"))
async def command_subscription(message: Message) -> None:
    user = message.from_user
    lang = message.from_user.language_code
    text = localization.get_text("SUBSCRIPTION_MESSAGE", lang)
    logger.debug(f"Sent main menu to user {message.from_user.id} with language {lang}")
    await message.answer(text, reply_markup=get_subscription_keyboard(lang))


@router.callback_query(F.data == "subscription")
async def callback_subscription(callback: CallbackQuery) -> None:
    user = callback.from_user
    lang = callback.from_user.language_code
    await callback.message.delete()
    text = localization.get_text("SUBSCRIPTION_MESSAGE", lang)
    logger.debug(f"Sent main menu to user {callback.from_user.id} with language {lang}")
    await callback.message.answer(text, reply_markup=get_subscription_keyboard(lang))


@router.callback_query(F.data.startswith("sub_"))
async def callback_subscription(callback: CallbackQuery) -> None:
    user = callback.from_user
    lang = callback.from_user.language_code
    # TODO: FSM


def register_handler(dp: Dispatcher) -> None:
    """
    Registers the router containing the subscription command and callback handlers.

    Args:
        dp (Dispatcher): The dispatcher to which the router will be added.
    """
    dp.include_router(router)
    logger.debug("Subscription handler registered.")
