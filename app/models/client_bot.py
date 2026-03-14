from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Numeric, Boolean
from sqlalchemy.sql import func
from app.models import Base


class ClientBot(Base):
    """Client bots table"""
    __tablename__ = "client_bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True, nullable=False)  # Removed ForeignKey
    bot_name = Column(String(255), nullable=False)
    bot_token = Column(String(255), nullable=False, unique=True)
    bot_username = Column(String(255), nullable=True)  # @username of the bot
    channel_id = Column(BigInteger, nullable=True)  # Changed from channel_link to channel_id
    manager_invite_link = Column(String(255), nullable=True)  # Permanent invite link for manager
    card_number = Column(String(20), nullable=True)
    oy_narx = Column(Numeric(10, 2), nullable=True)
    yil_narx = Column(Numeric(10, 2), nullable=True)
    cheksiz_narx = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), default="free")  # free, active, stopped
    process_id = Column(Integer, nullable=True)  # Bot process ID for stopping
    should_stop = Column(Boolean, default=False)  # False = running, True = should stop
    created_at = Column(DateTime(timezone=True), server_default=func.now())
