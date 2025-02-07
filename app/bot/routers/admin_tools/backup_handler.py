import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsAdmin
from app.bot.models import ServicesContainer
from app.bot.utils.constants import BACKUP_CREATED_TAG
from app.bot.utils.navigation import NavAdminTools
from app.config import DEFAULT_DATA_DIR, Config
from app.db.models import User

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(F.data == NavAdminTools.CREATE_BACKUP, IsAdmin())
async def callback_create_backup(
    callback: CallbackQuery,
    user: User,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"Admin {user.tg_id} initiated backup creation.")
    try:
        file = FSInputFile(
            path=f"{DEFAULT_DATA_DIR}/{config.database.NAME}.sqlite3",
            filename=f"backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3",
        )
        await services.notification.notify_developer(BACKUP_CREATED_TAG, document=file)
        await services.notification.show_popup(callback, _("backup:popup:success"))
        logger.info(f"Backup sent to developer: {config.bot.DEV_ID}")
    except FileNotFoundError:
        logger.error("Database file not found.")
        await services.notification.show_popup(callback, _("backup:popup:not_found"))
    except TelegramAPIError as exception:
        logger.error(f"Failed to send backup to developer: {exception}")
        await services.notification.show_popup(callback, _("backup:popup:failed"))
    except Exception as exception:
        logger.error(f"Unexpected error during backup creation: {exception}")
        await services.notification.show_popup(callback, _("backup:popup:error"))
