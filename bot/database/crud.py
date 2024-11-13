import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.future import select

from bot.database.models import Subscription, User
from bot.database.session import AsyncSessionLocal


async def create_user(
    telegram_id: int, first_name: str, last_name: str, language_code: str
) -> User:
    async with AsyncSessionLocal() as db:
        user = User(
            id=str(uuid.uuid4()),
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            joined_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def get_user(telegram_id: int) -> User | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()


async def create_or_update_subscription(
    telegram_id: int, plan: str, duration_days: int
) -> Subscription:
    async with AsyncSessionLocal() as db:
        expiry_date = datetime.utcnow() + timedelta(days=duration_days)

        result = await db.execute(
            select(Subscription).where(Subscription.telegram_id == telegram_id)
        )
        subscription = result.scalars().first()

        if subscription:
            subscription.plan = plan
            subscription.expiry_date = expiry_date
            subscription.active = True
        else:
            subscription = Subscription(
                telegram_id=telegram_id, plan=plan, expiry_date=expiry_date, active=True
            )
            db.add(subscription)

        await db.commit()
        await db.refresh(subscription)
        return subscription


async def get_subscription(telegram_id: int) -> Subscription | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Subscription).where(Subscription.telegram_id == telegram_id)
        )
        return result.scalars().first()


async def delete_user(telegram_id: int) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_user(telegram_id)
        if user:
            await db.delete(user)
            await db.commit()
