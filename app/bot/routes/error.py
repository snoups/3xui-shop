import logging
import traceback

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import BufferedInputFile, ErrorEvent
from aiogram.utils.markdown import hbold, hcode

from app.config import Config

logger = logging.getLogger(__name__)
router = Router(name=__name__)


def split_text(text: str, chunk_size: int = 4096) -> list[str]:
    """
    Splits a string into smaller chunks.

    Arguments:
        text (str): The string to split.
        chunk_size (int): The maximum size of each chunk.

    Returns:
        list[str]: A list of string chunks.
    """
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


@router.errors(ExceptionTypeFilter(Exception))
async def errors_handler(
    event: ErrorEvent,
    bot: Bot,
    config: Config,
) -> bool:
    """
    Handles all uncaught exceptions during bot operation.

    Arguments:
        event (ErrorEvent): The event containing the exception and update details.
        bot (Bot): The bot instance.
        config (Config): Configuration object for the bot.

    Returns:
        bool: True to stop further error handling, False to continue.
    """
    if isinstance(event.exception, TelegramForbiddenError):
        logger.info(f"User {event.update.message.from_user.id} blocked the bot.")
        return True

    logger.exception(f"Update: {event.update}\nException: {event.exception}")

    if not config.bot.DEV_ID:
        return True

    try:
        document_message = await bot.send_document(
            chat_id=config.bot.DEV_ID,
            document=BufferedInputFile(
                traceback.format_exc().encode(),
                filename=f"error_{event.update.update_id}.txt",
            ),
            caption=f"{hbold(type(event.exception).__name__)}: {str(event.exception)[:1021]}...",
        )

        update_json = event.update.model_dump_json(indent=2, exclude_none=True)
        for chunk in split_text(update_json):
            await document_message.reply(text=hcode(chunk))

    except TelegramBadRequest as exception:
        logger.warning(f"Failed to send error details: {exception}")
    except Exception as exception:
        logger.error(f"Unexpected error in error handler: {exception}")

    return True
