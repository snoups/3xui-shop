from aiogram import Router
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User

router = Router()


@router.my_chat_member()
async def my_chat_member(update: ChatMemberUpdated, session: AsyncSession, user: User) -> None:
    """
    Handle updates of the bot chat member status.

    :param update: The chat member update event.
    :param session: The asynchronous SQLAlchemy session.
    :param user: The user object from database.
    :return: None
    """
    await User.update(session, user_id=user.user_id, state=update.new_chat_member.status)
