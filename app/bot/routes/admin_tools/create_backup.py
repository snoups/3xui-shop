import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin, IsPrivate
from app.bot.navigation import NavAdminTools
from app.config import DEFAULT_DATA_DIR, load_config

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.CREATE_BACKUP, IsPrivate(), IsAdmin())
async def callback_create_backup(callback: CallbackQuery) -> None:
    """
    Handler for creating backups.

    Arguments:
        callback (CallbackQuery): The incoming callback query.
    """
    logger.info(f"Admin {callback.from_user.id} initiated backup creation.")
    config = load_config()
    try:
        file = FSInputFile(
            path=f"{DEFAULT_DATA_DIR}/{config.database.NAME}.sqlite3",
            filename=f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3",
        )
        await callback.bot.send_document(chat_id=config.bot.DEV_ID, document=file)
        await callback.answer(_("✅ Backup sent successfully."), show_alert=True)
        logger.info(f"Backup sent to developer: {config.bot.DEV_ID}")
    except FileNotFoundError:
        logger.error("Database file not found.")
        await callback.answer(_("❌ Database file not found."), show_alert=True)
    except TelegramAPIError as exception:
        logger.error(f"Failed to send backup to developer: {exception}")
        await callback.answer(_("❌ Failed to send backup."), show_alert=True)
    except Exception as exception:
        logger.error(f"Unexpected error during backup creation: {exception}")
        await callback.answer(_("❌ An error occurred during backup."), show_alert=True)
