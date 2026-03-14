import asyncio
import logging
from sqlalchemy import text
from app.database import engine
from app.models import Base

logger = logging.getLogger(__name__)


async def init_db(drop_all: bool = False):
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        if drop_all:
            # Drop all existing tables
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("🗑️ Eski jadvallar o'chirildi!")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database jadvallari yaratildi!")


async def check_db():
    """Check if database is available"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database bog'lanishi muvaffaqiyatli!")
        return True
    except Exception as e:
        logger.error(f"❌ Database bog'lanish xatosi: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(init_db(drop_all=True))
