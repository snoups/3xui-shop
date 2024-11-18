import hashlib
from datetime import datetime, timezone

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import create_async_engine

from bot.database.base import Base
from bot.database.models import User
from bot.utils.config import config

engine = create_async_engine(config.db.url)


async def create_user(
    telegram_id: int, first_name: str, last_name: str, language_code: str
) -> User:
    async with engine.connect() as conn:
        user: User | None = await get_user(telegram_id)

        if user:
            return

        hash = hashlib.md5(str(telegram_id).encode()).hexdigest()
        joined_at = datetime.now(timezone.utc)
        sql_query = insert(User).values(
            vpn_id=hash,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            joined_at=joined_at,
        )
        await conn.execute(sql_query)
        await conn.commit()


async def get_user(telegram_id: int) -> User | None:
    async with engine.connect() as conn:
        sql_query = select(User).where(User.telegram_id == telegram_id)
        result: User | None = (await conn.execute(sql_query)).fetchone()
        return result


async def delete_user(telegram_id: int) -> None:
    async with engine.connect() as conn:
        user: User | None = get_user(telegram_id)
        if user:
            sql_query = delete(User).where(User.telegram_id == telegram_id)
            await conn.execute(sql_query)
            await conn.commit()
