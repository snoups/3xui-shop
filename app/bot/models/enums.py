from enum import Enum


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REFUNDED = "refunded"
