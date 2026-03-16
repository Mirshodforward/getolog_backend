from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Numeric
from sqlalchemy.sql import func
from app.models import Base


class Spending(Base):
    """
    Balans sarflanish jadvali - client va userlar uchun umumiy

    role: "client" yoki "user"
    - client: Premium obuna uchun to'lov
    - user: Bot orqali obuna uchun to'lov (1 oy, 1 yil, cheksiz)
    """
    __tablename__ = "spendings"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False, index=True)  # "client" yoki "user"
    user_id = Column(BigInteger, nullable=False, index=True)  # Telegram user ID
    username = Column(String(255), nullable=True)  # Telegram username (agar bor bo'lsa)
    amount = Column(Numeric(10, 2), nullable=False)  # Yechilgan summa
    spend = Column(String(100), nullable=False)  # Nima uchun sarflangan: "1 oy", "1 yil", "cheksiz", "premium"
    admin_id = Column(BigInteger, nullable=True, index=True)  # User uchun - bot egasining ID si
    bot_username = Column(String(255), nullable=True)  # User uchun - bot_username
    created_at = Column(DateTime(timezone=True), server_default=func.now())
