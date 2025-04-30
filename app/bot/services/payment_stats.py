import logging
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.models import SubscriptionData
from app.bot.utils.constants import TransactionStatus
from app.db.models import Transaction

logger = logging.getLogger(__name__)


class PaymentStatsService:
    """Service for tracking payment statistics and revenue from transaction records."""

    def __init__(self, session_factory: async_sessionmaker) -> None:
        """
        Initialize PaymentStatsService.

        Args:
            session_factory: SQLAlchemy async session maker
        """
        self.session_factory = session_factory
        logger.debug("PaymentStatsService initialized")

    async def get_user_payment_stats(
        self,
        user_id: int,
        session: Optional[AsyncSession] = None,
        payment_method_currencies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, float]:
        """
        Calculate total payments by currency for a specific user using transactions table.

        Args:
            user_id: Telegram user ID
            session: Optional existing database session
            payment_method_currencies: Dictionary mapping payment methods to currency codes

        Returns:
            Dict mapping currency codes to total amounts
        """

        async def _get_stats(s: AsyncSession) -> Dict[str, float]:
            # Get completed transactions for this user
            query = await s.execute(
                select(Transaction).where(
                    Transaction.tg_id == user_id, Transaction.status == TransactionStatus.COMPLETED
                )
            )
            transactions = query.scalars().all()

            results = {}
            for tx in transactions:
                try:
                    data = SubscriptionData.unpack(tx.subscription)
                    payment_method = data.state.value

                    currency = None
                    if payment_method_currencies:
                        for method, curr in payment_method_currencies.items():
                            if method in payment_method:
                                currency = curr
                                break
                    else:
                        logger.warning(
                            f"payment_method_currencies not provided for payment_method: {payment_method}"
                        )
                        continue

                    if not currency:
                        logger.warning(f"Unknown payment method: {payment_method}")
                        continue

                    if currency not in results:
                        results[currency] = 0
                    results[currency] += float(data.price)
                except Exception as e:
                    logger.warning(
                        f"Could not parse subscription data: {tx.subscription}. Error: {e}"
                    )

            return results

        if session:
            return await _get_stats(session)
        else:
            async with self.session_factory() as session:
                return await _get_stats(session)

    async def get_total_revenue_stats(
        self,
        session: Optional[AsyncSession] = None,
        payment_method_currencies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, float]:
        """
        Calculate total revenue across all completed transactions by currency.

        Args:
            session: Optional existing database session
            payment_method_currencies: Dictionary mapping payment methods to currency codes

        Returns:
            Dict mapping currency codes to total amounts
        """

        async def _get_stats(s: AsyncSession) -> Dict[str, float]:
            query = await s.execute(
                select(Transaction).where(Transaction.status == TransactionStatus.COMPLETED)
            )
            transactions = query.scalars().all()

            results = {}
            for tx in transactions:
                try:
                    data = SubscriptionData.unpack(tx.subscription)
                    payment_method = data.state.value

                    currency = None
                    if payment_method_currencies:
                        for method, curr in payment_method_currencies.items():
                            if method in payment_method:
                                currency = curr
                                break
                    else:
                        logger.warning(
                            f"payment_method_currencies not provided for payment_method: {payment_method}"
                        )
                        continue

                    if not currency:
                        logger.warning(f"Unknown payment method: {payment_method}")
                        continue

                    if currency not in results:
                        results[currency] = 0
                    results[currency] += float(data.price)
                except Exception as e:
                    logger.warning(
                        f"Could not parse subscription data: {tx.subscription}. Error: {e}"
                    )

            return results

        if session:
            return await _get_stats(session)
        else:
            async with self.session_factory() as session:
                return await _get_stats(session)
