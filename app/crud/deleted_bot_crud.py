from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.deleted_bot import DeletedBot
from app.models.client_bot import ClientBot
from app.models.user import User


async def get_bot_users_count(session: AsyncSession, admin_id: int) -> int:
    """Get count of users registered via bot (by admin_id)"""
    stmt = select(func.count()).select_from(User).where(User.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar() or 0


async def create_deleted_bot(session: AsyncSession, bot: ClientBot, users_count: int, reason: str = None) -> DeletedBot:
    """Archive a bot to deleted_bots table before deletion"""
    deleted_bot = DeletedBot(
        original_bot_id=bot.id,
        user_id=bot.user_id,
        bot_username=bot.bot_username,
        bot_token=bot.bot_token,
        channel_id=bot.channel_id,
        manager_invite_link=bot.manager_invite_link,
        card_number=bot.card_number,
        oy_narx=bot.oy_narx,
        yil_narx=bot.yil_narx,
        cheksiz_narx=bot.cheksiz_narx,
        status=bot.status,
        registered_users_count=users_count,
        bot_created_at=bot.created_at,
        deletion_reason=reason
    )
    session.add(deleted_bot)
    await session.commit()
    await session.refresh(deleted_bot)
    return deleted_bot


async def delete_client_bot(session: AsyncSession, bot_id: int) -> bool:
    """Delete bot from client_bots table"""
    stmt = select(ClientBot).where(ClientBot.id == bot_id)
    result = await session.execute(stmt)
    bot = result.scalar_one_or_none()
    
    if bot:
        await session.delete(bot)
        await session.commit()
        return True
    return False


async def get_deleted_bots_by_user(session: AsyncSession, user_id: int):
    """Get all deleted bots for a user"""
    stmt = select(DeletedBot).where(DeletedBot.user_id == user_id).order_by(DeletedBot.deleted_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_deleted_bots(session: AsyncSession):
    """Get all deleted bots"""
    stmt = select(DeletedBot).order_by(DeletedBot.deleted_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()
