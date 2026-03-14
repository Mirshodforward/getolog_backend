from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


async def get_or_create_user(session: AsyncSession, user_id: int, username: str = None, name: str = None, language: str = "uz"):
    """Get or create user"""
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        user = User(user_id=user_id, username=username, name=name, language=language)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    return user


async def get_user_by_id(session: AsyncSession, user_id: int):
    """Get user by telegram id"""
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_all_users(session: AsyncSession):
    """Barcha userlarni olish (broadcast uchun)"""
    stmt = select(User)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_user_ids(session: AsyncSession):
    """Barcha userlarning user_id larini olish (broadcast uchun)"""
    stmt = select(User.user_id)
    result = await session.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def get_users_grouped_by_admin(session: AsyncSession):
    """
    Userlarni admin_id bo'yicha guruhlab olish (broadcast uchun).
    Returns: dict {admin_id: [user_id1, user_id2, ...]}
    """
    stmt = select(User.admin_id, User.user_id)
    result = await session.execute(stmt)

    grouped = {}
    for row in result.fetchall():
        admin_id = row[0]
        user_id = row[1]
        if admin_id not in grouped:
            grouped[admin_id] = []
        grouped[admin_id].append(user_id)

    return grouped
