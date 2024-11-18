from sqlalchemy import Column, DateTime, Integer, String

from bot.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    vpn_id = Column(String)
    telegram_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    joined_at = Column(DateTime)
