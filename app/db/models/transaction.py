from datetime import datetime

from sqlalchemy import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ._base import Base
from .user import User


class Transaction(Base):
    """
    Model representing the Transaction table in the database.

    This model is used to store transaction details related to a user's subscription or payment.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    payment_id: Mapped[str] = mapped_column(String(length=64), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(length=16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    @classmethod
    async def get_by_user(cls, session: AsyncSession, user_id: int) -> list["Transaction"]:
        """
        Get all transactions for a specific user.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The user's unique ID.

        Returns:
            list[Transaction]: A list of transactions for the user.
        """
        result = await session.execute(select(Transaction).filter(Transaction.user_id == user_id))
        return result.scalars().all()

    @classmethod
    async def create_transaction(
        cls,
        session: AsyncSession,
        user_id: int,
        payment_id: str,
        amount: float,
        status: str,
    ) -> "Transaction":
        """
        Create a new transaction in the database.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            user_id (int): The unique user ID.
            payment_id (str): The unique payment ID for this transaction.
            amount (float): The amount of the transaction.
            status (str): The status of the transaction (e.g., "completed").

        Returns:
            Transaction: The created transaction object.
        """
        transaction = Transaction(
            user_id=user_id,
            payment_id=payment_id,
            amount=amount,
            status=status,
        )
        session.add(transaction)
        await session.commit()
        return transaction

    @classmethod
    async def get(cls, session: AsyncSession, transaction_id: int) -> "Transaction | None":
        """
        Get a transaction by its ID.

        Arguments:
            session (AsyncSession): The asynchronous SQLAlchemy session.
            transaction_id (int): The unique transaction ID.

        Returns:
            Transaction | None: The transaction object if found, or None if not found.
        """
        result = await session.execute(
            select(Transaction).filter(Transaction.payment_id == transaction_id)
        )
        return result.scalar_one_or_none()
