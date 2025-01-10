from datetime import datetime

from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base
from .user import User


class Transaction(Base):
    """
    Model representing the Transaction table in the database.

    This model stores transaction details for a user's subscription or payment,
    linking to a specific user and including payment info, amount, status, and timestamps.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    plan: Mapped[str] = mapped_column(String(length=64), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(length=16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    @classmethod
    async def get(cls, session: AsyncSession, payment_id: int) -> "Transaction | None":
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
    async def get_by_user(cls, session: AsyncSession, user_id: int) -> list["Transaction"]:
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
    async def create(cls, session: AsyncSession, payment_id: str, **kwargs) -> "Transaction | None":
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
                return None

        return transaction

    @classmethod
    async def update(cls, session: AsyncSession, payment_id: str, **kwargs) -> "Transaction | None":
        """
        Update an existing transaction in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            payment_id (str): The unique payment ID for the transaction.
            kwargs (dict): Fields to update (e.g., status, amount).

        Returns:
            Transaction | None: The updated transaction object if successful, or None if not found.

        Example:
            updated_transaction = await Transaction.update(session, payment_id="abc123",
                status="completed", amount=100.0)
        """
        filter = [Transaction.payment_id == payment_id]
        query = await session.execute(select(Transaction).where(*filter))
        transaction = query.scalar_one_or_none()

        if not transaction:
            return None

        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            return None

        return transaction
