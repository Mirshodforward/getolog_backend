from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Numeric
from sqlalchemy.sql import func
from app.models import Base


class Transaction(Base):
    """Transaction history for balance top-ups and payments"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(BigInteger, nullable=True)  # Admin who approved/rejected
    user_id = Column(BigInteger, index=True, nullable=False)  # User who made transaction
    username = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)  # Transaction amount
    role = Column(String(50), nullable=False, default="topup")  # topup, payment, refund
    status = Column(String(50), nullable=False, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
