from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.utils.localization import localization
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()
router = Router(name="subscription")


@router.message(Command("subscription"))
async def command_subscription(message: Message) -> None:
    pass


@router.callback_query(F.data == "subscription")
async def callback_subscription(callback: CallbackQuery) -> None:
    pass


def register_handler(dp: Dispatcher) -> None:
    """
    Registers the router containing the subscription command and callback handlers.

    Args:
        dp (Dispatcher): The dispatcher to which the router will be added.
    """
    dp.include_router(router)
    logger.debug("Subscription handler registered.")
