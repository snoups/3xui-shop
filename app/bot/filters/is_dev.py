import logging

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.types import User as TelegramUser

logger = logging.getLogger(__name__)


class IsDev(BaseFilter):
    developer_id: int

    async def __call__(
        self,
        event: TelegramObject | None = None,
        user_id: int | None = None,
    ) -> bool:
        if user_id:
            return user_id == self.developer_id

        user: TelegramUser | None = event.from_user

        if not user:
            return False

        return user.id == self.developer_id

    @classmethod
    def set_developer(cls, developer_id: int) -> None:
        cls.developer_id = developer_id
        logger.info(f"Developer set: {developer_id}")
