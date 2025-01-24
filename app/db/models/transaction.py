import logging
from datetime import datetime
from typing import Self

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.types import Enum

from app.bot.navigation import TransactionStatus

from . import Base

logger = logging.getLogger(__name__)


class Transaction(Base):
    """
    Represents the Transaction table in the database.

    Attributes:
        id (int): The unique transaction ID (primary key).
        tg_id (int): The Telegram user ID associated with the transaction (foreign key).
        payment_id (str): The unique payment ID for the transaction.
        subscription (str): The name of the subscription plan for the transaction.
        status (TransactionStatus): The current status of the transaction
            (e.g., pending, failed, completed).
        created_at (datetime): The timestamp when the transaction was created.
        updated_at (datetime): The timestamp when the transaction was last updated.
        user (User): The related user object.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)

    subscription: Mapped[str] = mapped_column(String(length=255), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")  # type: ignore

    def __repr__(self) -> str:
        """
        Represents the Transaction object as a string.

        Returns:
            str: A string representation of the Transaction object.
        """
        return (
            f"<Transaction(id={self.id}, tg_id={self.tg_id}, payment_id='{self.payment_id}', "
            f"subscription='{self.subscription}', status='{self.status}', "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

    @classmethod
    async def get(cls, session: AsyncSession, payment_id: str) -> Self | None:
        """
        Retrieve a transaction by its payment ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.

        Returns:
            Transaction | None: The transaction object if found, otherwise None.

        Example:
            transaction = await Transaction.get(session, payment_id="abc123")
        """
        filter = [Transaction.payment_id == payment_id]
        query = await session.execute(
            select(Transaction).options(selectinload(Transaction.user)).where(*filter)
        )
        return query.scalar_one_or_none()

    @classmethod
    async def get_by_user(cls, session: AsyncSession, tg_id: int) -> list[Self]:
        """
        Retrieve all transactions for a specific user.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            tg_id (int): The unique Telegram user ID for the transactions.

        Returns:
            list[Transaction]: A list of transactions for the user, or an empty list if none.

        Example:
            transactions = await Transaction.get_by_user(session, tg_id=123456)
        """
        filter = [Transaction.tg_id == tg_id]
        query = await session.execute(
            select(Transaction).options(selectinload(Transaction.user)).where(*filter)
        )
        return query.scalars().all()

    @classmethod
    async def create(cls, session: AsyncSession, payment_id: str, **kwargs) -> Self | None:
        """
        Create a new transaction.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.
            kwargs (dict): Additional attributes for creating the transaction.

        Returns:
            Transaction | None: The created transaction object if successful,
                or None if creation failed.

        Example:
            transaction = await Transaction.create(session, payment_id="abc123",
                tg_id=123, subscription="plan", status="completed")
        """
        transaction = await Transaction.get(session, payment_id)

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
        Update an existing transaction.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.
            kwargs (dict): Fields to update (e.g., status).

        Example:
            await Transaction.update(session, payment_id="1", status="completed")
        """
        filter = [Transaction.payment_id == payment_id]
        await session.execute(update(Transaction).where(*filter).values(**kwargs))
        await session.commit()
