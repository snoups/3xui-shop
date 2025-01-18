import logging
from datetime import datetime
from typing import Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from . import Base

logger = logging.getLogger(__name__)


class Transaction(Base):
    """
    Model representing the Transaction table in the database.

    Attributes:
        id (int): The unique transaction ID (primary key).
        user_id (int): The ID of the user associated with the transaction (foreign key).
        payment_id (str): The unique payment ID for the transaction.
        plan (str): The name of the subscription plan for the transaction.
        status (TransactionStatus): The current status of the transaction (pending, failed, etc.).
        created_at (datetime): The timestamp when the transaction was created.
        updated_at (datetime): The timestamp when the transaction was last updated.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)
    subscription: Mapped[str] = mapped_column(String(length=255), nullable=False)
    status: Mapped[str] = mapped_column(String(length=16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, user_id='{self.user_id}', payment_id={self.payment_id}, "
            f"subscription={self.subscription}, status={self.status}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, payment_id: str) -> Self | None:
        """
        Get a transaction by its payment ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID.

        Returns:
            Transaction | None: The transaction object if found, or None if not found.

        Example:
            transaction = await Transaction.get(session, payment_id="abc123")
        """
        filter = [Transaction.payment_id == payment_id]
        query = await session.execute(select(Transaction).where(*filter))
        return query.scalar_one_or_none()

    @classmethod
    async def get_by_user(cls, session: AsyncSession, user_id: int) -> list[Self]:
        """
        Get all transactions for a specific user.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique user ID to fetch transactions for.

        Returns:
            list[Transaction]: A list of transactions for the user.

        Example:
            transactions = await Transaction.get_by_user(session, user_id=123456)
        """
        filter = [Transaction.user_id == user_id]
        query = await session.execute(select(Transaction).where(*filter))
        return query.scalars().all()

    @classmethod
    async def create(cls, session: AsyncSession, payment_id: str, **kwargs) -> Self | None:
        """
        Create a new transaction in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.
            kwargs (dict): Additional attributes for the transaction
                (e.g., user_id, amount, status).

        Returns:
            Transaction | None: The created transaction object if successful,
                or None if creation failed.

        Example:
            transaction = await Transaction.create(session, payment_id="abc123",
                user_id=123, amount=50.0, status="completed")
        """
        filter = [Transaction.payment_id == payment_id]
        query = await session.execute(select(Transaction).where(*filter))
        transaction = query.scalar_one_or_none()

        if transaction is None:
            transaction = Transaction(payment_id=payment_id, **kwargs)
            session.add(transaction)

            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                logger.error(f"Error occurred while creating transaction {payment_id}")
                return None

        return transaction

    @classmethod
    async def update(cls, session: AsyncSession, payment_id: str, **kwargs) -> None:
        """
        Update an existing transaction in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.
            kwargs (dict): Fields to update (e.g., status, amount).

        Example:
            await Transaction.update(session, payment_id="abc123", status="completed", amount=100)
        """
        filter = [Transaction.payment_id == payment_id]
        await session.execute(update(Transaction).where(*filter).values(**kwargs))
        await session.commit()
