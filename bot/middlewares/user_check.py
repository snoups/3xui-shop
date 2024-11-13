from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.database import crud


class UserCheckMiddleware(BaseMiddleware):
    """
    Middleware to check if the user exists in the database.
    If the user doesn't exist, it will create a new user.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        first_name = event.from_user.first_name
        last_name = event.from_user.last_name
        language_code = event.from_user.language_code

        user = await crud.get_user(telegram_id=user_id)
        if not user:
            await crud.create_user(
                telegram_id=user_id,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
            )

        return await handler(event, data)
