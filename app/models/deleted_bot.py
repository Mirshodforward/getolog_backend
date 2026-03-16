from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Numeric, Text
from sqlalchemy.sql import func
from app.models import Base


class DeletedBot(Base):
    """Deleted bots archive table"""
    __tablename__ = "deleted_bots"

    id = Column(Integer, primary_key=True, index=True)
    original_bot_id = Column(Integer, nullable=False)  # Original bot ID from client_bots
    user_id = Column(BigInteger, index=True, nullable=False)  # Bot owner
    bot_token = Column(String(255), nullable=False)
    bot_username = Column(String(255), nullable=True)
    channel_id = Column(BigInteger, nullable=True)
    manager_invite_link = Column(String(255), nullable=True)
    card_number = Column(String(20), nullable=True)
    oy_narx = Column(Numeric(10, 2), nullable=True)
    yil_narx = Column(Numeric(10, 2), nullable=True)
    cheksiz_narx = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), nullable=True)  # Status before deletion
    registered_users_count = Column(Integer, default=0)  # Number of users registered via this bot
    bot_created_at = Column(DateTime(timezone=True), nullable=True)  # Original creation date
    deleted_at = Column(DateTime(timezone=True), server_default=func.now())  # Deletion date
    deletion_reason = Column(Text, nullable=True)  # Optional reason for deletion
