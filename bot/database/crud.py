from datetime import datetime, timedelta, timezone

from sqlalchemy.future import select

from database.models import Subscription, User
from database.session import AsyncSessionLocal


async def create_user(
    user_id: int, username: str, first_name: str, last_name: str, language_code: str
) -> User:
    joined_at = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            joined_at=joined_at,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def get_user(user_id: int) -> User | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()


async def create_or_update_subscription(
    user_id: int, plan: str, duration_days: int
) -> Subscription:
    async with AsyncSessionLocal() as db:
        expiry_date = datetime.utcnow() + timedelta(days=duration_days)

        result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
        subscription = result.scalars().first()

        if subscription:
            subscription.plan = plan
            subscription.expiry_date = expiry_date
            subscription.active = True
        else:
            subscription = Subscription(
                user_id=user_id, plan=plan, expiry_date=expiry_date, active=True
            )
            db.add(subscription)

        await db.commit()
        await db.refresh(subscription)
        return subscription


async def get_subscription(user_id: int) -> Subscription | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
        return result.scalars().first()


async def delete_user(user_id: int) -> None:
    async with AsyncSessionLocal() as db:
        user = await get_user(user_id)
        if user:
            await db.delete(user)
            await db.commit()
