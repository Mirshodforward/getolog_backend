from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, Numeric
from sqlalchemy.sql import func
from app.models import Base


class Client(Base):
    """Clients table"""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True, nullable=False)  # Removed ForeignKey
    username = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    plan_type = Column(String(50), nullable=True) #free, standart, biznes
    plan_start_date = Column(DateTime(timezone=True), nullable=True)
    plan_end_date = Column(DateTime(timezone=True), nullable=True)
    oylik_obuna = Column(Boolean, default=False)
    switch_ads = Column(Boolean, default=True)
    balance = Column(Numeric(10, 2), default=0)
    terms = Column(Boolean, default=False)
    language = Column(String(10), default="uz")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
