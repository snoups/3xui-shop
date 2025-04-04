import logging
from typing import Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.utils.constants import TransactionStatus
from app.db.models import Transaction, User

logger = logging.getLogger(__name__)


class InviteStatsService:
    """Service for collecting and analyzing invite link statistics."""

    def __init__(self, session_maker: async_sessionmaker, payment_stats_service) -> None:
        """
        Initialize InviteStatsService.

        Args:
            session_maker: SQLAlchemy async session maker
            payment_stats_service: Instance of PaymentStatsService for payment data retrieval
        """
        self.session_maker = session_maker
        self.payment_stats = payment_stats_service
        logger.debug("InviteStatsService initialized")

    async def get_detailed_stats(
        self, invite_name: str, session: Optional[AsyncSession] = None
    ) -> Dict[str, any]:
        """
        Get detailed statistics for a specific invite link.

        Args:
            invite_name: Name of the invite link
            session: Optional existing database session

        Returns:
            Dict containing detailed statistics
        """
        async def _get_stats(s: AsyncSession) -> Dict[str, any]:
            # Get users who came from this invite
            users_query = await s.execute(
                select(User).where(User.source_invite_name == invite_name)
            )
            users = users_query.scalars().all()

            if not users:
                return {
                    "revenue": {},
                    "users_count": 0,
                    "trial_users_count": 0,
                    "paid_users_count": 0,
                    "repeat_customers_count": 0
                }

            user_ids = [user.tg_id for user in users]
            trial_users_count = sum(1 for user in users if user.is_trial_used)

            # Get users with transactions
            tx_users_query = await s.execute(
                select(Transaction.tg_id).where(
                    Transaction.tg_id.in_(user_ids),
                    Transaction.status == TransactionStatus.COMPLETED
                ).distinct()
            )
            paid_users = set(user_id for user_id, in tx_users_query)

            # Get users with more than one transaction
            repeat_users_query = await s.execute(
                select(Transaction.tg_id).where(
                    Transaction.tg_id.in_(user_ids),
                    Transaction.status == TransactionStatus.COMPLETED
                ).group_by(Transaction.tg_id).having(func.count(Transaction.id) > 1)
            )
            repeat_customers = set(user_id for user_id, in repeat_users_query)

            # Get revenue totals from payment stats service
            all_revenue = {}
            for user_id in user_ids:
                user_revenue = await self.payment_stats.get_user_payment_stats(user_id, s)
                for currency, amount in user_revenue.items():
                    if currency not in all_revenue:
                        all_revenue[currency] = 0
                    all_revenue[currency] += amount

            return {
                "revenue": all_revenue,
                "users_count": len(users),
                "trial_users_count": trial_users_count,
                "paid_users_count": len(paid_users),
                "repeat_customers_count": len(repeat_customers)
            }

        if session:
            return await _get_stats(session)
        else:
            async with self.session_maker() as session:
                return await _get_stats(session)
