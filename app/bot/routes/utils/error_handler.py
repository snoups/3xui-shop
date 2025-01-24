import logging
import traceback

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import BufferedInputFile, ErrorEvent
from aiogram.utils.markdown import hbold, hcode

from app.config import Config
from app.utils import split_text

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.errors(ExceptionTypeFilter(Exception))
async def errors_handler(
    event: ErrorEvent,
    bot: Bot,
    config: Config,
) -> bool:
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
