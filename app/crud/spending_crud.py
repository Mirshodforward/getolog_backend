from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.sql import func
from decimal import Decimal
from app.models.spending import Spending


async def create_spending(
    session: AsyncSession,
    role: str,
    user_id: int,
    amount: Decimal,
    spend: str,
    username: str = None,
    admin_id: int = None,
    bot_name: str = None
) -> Spending:
    """
    Yangi sarflanish yozuvini yaratish

    Args:
        role: "client" yoki "user"
        user_id: Telegram user ID
        amount: Yechilgan summa
        spend: Nima uchun sarflangan (1 oy, 1 yil, cheksiz, premium)
        username: Telegram username (ixtiyoriy)
        admin_id: User uchun - bot egasining ID si
        bot_name: User uchun - bot nomi
    """
    spending = Spending(
        role=role,
        user_id=user_id,
        username=username,
        amount=amount,
        spend=spend,
        admin_id=admin_id,
        bot_name=bot_name
    )
    session.add(spending)
    await session.commit()
    await session.refresh(spending)
    return spending


async def create_client_spending(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    spend: str = "premium",
    username: str = None
) -> Spending:
    """
    Client uchun sarflanish yaratish (premium obuna)
    """
    return await create_spending(
        session=session,
        role="client",
        user_id=user_id,
        amount=amount,
        spend=spend,
        username=username
    )


async def create_user_spending(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    spend: str,
    admin_id: int,
    bot_name: str = None,
    username: str = None
) -> Spending:
    """
    User uchun sarflanish yaratish (obuna sotib olish)

    Args:
        spend: "1 oy", "1 yil", "cheksiz"
    """
    return await create_spending(
        session=session,
        role="user",
        user_id=user_id,
        amount=amount,
        spend=spend,
        username=username,
        admin_id=admin_id,
        bot_name=bot_name
    )


async def get_spendings_by_user(session: AsyncSession, user_id: int, role: str = None):
    """
    User yoki client ning barcha sarflanishlarini olish
    """
    stmt = select(Spending).where(Spending.user_id == user_id)
    if role:
        stmt = stmt.where(Spending.role == role)
    stmt = stmt.order_by(desc(Spending.created_at))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_spendings_by_admin(session: AsyncSession, admin_id: int):
    """
    Admin (bot egasi) ning botidan olingan barcha sarflanishlarni olish
    """
    stmt = select(Spending).where(
        Spending.admin_id == admin_id,
        Spending.role == "user"
    ).order_by(desc(Spending.created_at))
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_spendings(session: AsyncSession, role: str = None, limit: int = 100, offset: int = 0):
    """
    Barcha sarflanishlarni olish (pagination bilan)
    """
    stmt = select(Spending)
    if role:
        stmt = stmt.where(Spending.role == role)
    stmt = stmt.order_by(desc(Spending.created_at)).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_total_spending_by_user(session: AsyncSession, user_id: int, role: str = None) -> Decimal:
    """
    User yoki client ning umumiy sarflanish summasi
    """
    stmt = select(func.coalesce(func.sum(Spending.amount), 0)).where(Spending.user_id == user_id)
    if role:
        stmt = stmt.where(Spending.role == role)
    result = await session.execute(stmt)
    return result.scalar()


async def get_total_spending_by_admin(session: AsyncSession, admin_id: int) -> Decimal:
    """
    Admin (bot egasi) ning botidan olingan umumiy daromad
    """
    stmt = select(func.coalesce(func.sum(Spending.amount), 0)).where(
        Spending.admin_id == admin_id,
        Spending.role == "user"
    )
    result = await session.execute(stmt)
    return result.scalar()


async def get_spending_stats(session: AsyncSession):
    """
    Umumiy statistika
    """
    # Clientlar sarfi
    client_total_stmt = select(func.coalesce(func.sum(Spending.amount), 0)).where(
        Spending.role == "client"
    )
    client_total = await session.execute(client_total_stmt)

    # Userlar sarfi
    user_total_stmt = select(func.coalesce(func.sum(Spending.amount), 0)).where(
        Spending.role == "user"
    )
    user_total = await session.execute(user_total_stmt)

    # Jami yozuvlar soni
    count_stmt = select(func.count(Spending.id))
    count = await session.execute(count_stmt)

    return {
        "client_total": client_total.scalar(),
        "user_total": user_total.scalar(),
        "total_records": count.scalar()
    }


async def get_spendings_count(session: AsyncSession, role: str = None) -> int:
    """
    Sarflanishlar sonini olish
    """
    stmt = select(func.count(Spending.id))
    if role:
        stmt = stmt.where(Spending.role == role)
    result = await session.execute(stmt)
    return result.scalar()
