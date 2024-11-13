from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    joined_at = Column(DateTime)

    subscriptions = relationship("Subscription", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, ForeignKey("users.telegram_id"))
    plan = Column(String)
    expiry_date = Column(DateTime)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")
