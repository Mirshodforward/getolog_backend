from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from app.models import Base


class User(Base):
    """Admin/Operator users"""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('user_id', 'bot_id', name='uq_user_bot'),
    )

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)
    bot_id = Column(Integer, nullable=True)
    username = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    duration = Column(String(255), nullable=True)
    balance = Column(Numeric(10, 2), default=0)
    status = Column(String(50), default="free")
    invite_link = Column(String(255), nullable=True)
    terms = Column(Integer, nullable=True)
    language = Column(String(10), default="uz")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
