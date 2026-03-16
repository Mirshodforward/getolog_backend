from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.client import Client


async def create_client(session: AsyncSession, user_id: int, username: str = None, phone_number: str = None, language: str = "uz"):
    """Create new client"""
    client = Client(
        user_id=user_id,
        username=username,
        phone_number=phone_number,
        language=language,
        plan_type="free"
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def get_client_by_user_id(session: AsyncSession, user_id: int):
    """Get client by telegram id"""
    stmt = select(Client).where(Client.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def update_client(session: AsyncSession, user_id: int, **kwargs):
    """Update client info"""
    stmt = select(Client).where(Client.user_id == user_id)
    result = await session.execute(stmt)
    client = result.scalars().first()

    if client:
        for key, value in kwargs.items():
            if hasattr(client, key):
                setattr(client, key, value)
        await session.commit()
        await session.refresh(client)

    return client


async def update_client_balance(session: AsyncSession, user_id: int, amount: float):
    """Update client balance by adding amount"""
    stmt = select(Client).where(Client.user_id == user_id)
    result = await session.execute(stmt)
    client = result.scalars().first()

    if client:
        current_balance = float(client.balance) if client.balance else 0
        client.balance = current_balance + amount
        await session.commit()
        await session.refresh(client)

    return client


async def get_all_clients(session: AsyncSession):
    """Barcha clientlarni olish (broadcast uchun)"""
    stmt = select(Client)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_client_user_ids(session: AsyncSession):
    """Barcha clientlarning user_id larini olish (broadcast uchun)"""
    stmt = select(Client.user_id)
    result = await session.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def update_client_language(session: AsyncSession, user_id: int, language: str):
    """Update client language"""
    stmt = select(Client).where(Client.user_id == user_id)
    result = await session.execute(stmt)
    client = result.scalars().first()

    if client:
        client.language = language
        await session.commit()
        await session.refresh(client)

    return client
