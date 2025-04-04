import logging
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.models import SubscriptionData
from app.bot.utils.constants import Currency, TransactionStatus
from app.db.models import Transaction

logger = logging.getLogger(__name__)


class PaymentStatsService:
    """Service for tracking payment statistics and revenue from transaction records."""

    def __init__(self, session_maker: async_sessionmaker) -> None:
        """
        Initialize PaymentStatsService.

        Args:
            session_maker: SQLAlchemy async session maker
        """
        self.session_maker = session_maker
        logger.debug("PaymentStatsService initialized")

    async def get_user_payment_stats(
        self, user_id: int, session: Optional[AsyncSession] = None
    ) -> Dict[str, float]:
        """
        Calculate total payments by currency for a specific user using transactions table.

        Args:
            user_id: Telegram user ID
            session: Optional existing database session

        Returns:
            Dict mapping currency codes to total amounts
        """
        async def _get_stats(s: AsyncSession) -> Dict[str, float]:
            # Get completed transactions for this user
            query = await s.execute(
                select(Transaction).where(
                    Transaction.tg_id == user_id,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            )
            transactions = query.scalars().all()

            results = {}
            for tx in transactions:
                try:
                    data = SubscriptionData.unpack(tx.subscription)
                    payment_method = data.state.value
                    currency = self._get_currency_from_payment_method(payment_method)

                    if not currency:
                        continue

                    if currency not in results:
                        results[currency] = 0
                    results[currency] += float(data.price)
                except Exception as e:
                    logger.warning(f"Could not parse subscription data: {tx.subscription}. Error: {e}")

            return results

        if session:
            return await _get_stats(session)
        else:
            async with self.session_maker() as session:
                return await _get_stats(session)

    async def get_total_revenue_stats(
        self, session: Optional[AsyncSession] = None
    ) -> Dict[str, float]:
        """
        Calculate total revenue across all completed transactions by currency.

        Args:
            session: Optional existing database session

        Returns:
            Dict mapping currency codes to total amounts
        """
        async def _get_stats(s: AsyncSession) -> Dict[str, float]:
            query = await s.execute(
                select(Transaction).where(
                    Transaction.status == TransactionStatus.COMPLETED
                )
            )
            transactions = query.scalars().all()

            results = {}
            for tx in transactions:
                try:
                    data = SubscriptionData.unpack(tx.subscription)
                    payment_method = data.state.value
                    currency = self._get_currency_from_payment_method(payment_method)

                    if not currency:
                        continue

                    if currency not in results:
                        results[currency] = 0
                    results[currency] += float(data.price)
                except Exception as e:
                    logger.warning(f"Could not parse subscription data: {tx.subscription}. Error: {e}")

            return results

        if session:
            return await _get_stats(session)
        else:
            async with self.session_maker() as session:
                return await _get_stats(session)

    def _get_currency_from_payment_method(self, payment_method: str) -> Optional[str]:
        """
        Extract currency code from payment method.

        Args:
            payment_method: Payment method string (e.g., 'pay_yookassa')

        Returns:
            Currency code or None if not recognized
        """
        method_to_currency = {
            'pay_yookassa': 'RUB',
            'pay_yoomoney': 'RUB',
            'pay_cryptomus': 'USD',
            'pay_heleket': 'USD',
            'pay_telegram_stars': 'XTR'
        }

        for method, currency in method_to_currency.items():
            if method in payment_method:
                return currency

        return None
