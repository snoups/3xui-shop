import logging

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser

from .is_dev import IsDev

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    admins_ids: list[int] = []

    async def __call__(self, event: TelegramObject) -> bool:
        user: TelegramUser | None = event.from_user

        if not user:
            return False

        is_dev = await IsDev()(event)
        return user.id in self.admins_ids or is_dev

    @classmethod
    def set_admins(cls, admins_ids: list[int]) -> None:
        cls.admins_ids = admins_ids
        logger.info(f"Admins set: {admins_ids}")
