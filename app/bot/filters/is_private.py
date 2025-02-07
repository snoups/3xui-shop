from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Chat


class IsPrivate(BaseFilter):
    async def __call__(self, event_chat: Chat) -> bool:
        return event_chat.type == ChatType.PRIVATE
