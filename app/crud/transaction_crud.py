from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction


async def create_transaction(
    session: AsyncSession,
    user_id: int,
    username: str,
    amount: float,
    role: str = "topup",
    status: str = "pending"
):
    """Create new transaction"""
    transaction = Transaction(
        user_id=user_id,
        username=username,
        amount=amount,
        role=role,
        status=status
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


async def update_transaction_status(
    session: AsyncSession,
    transaction_id: int,
    status: str,
    admin_id: int = None
):
    """Update transaction status (approve/reject)"""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await session.execute(stmt)
    transaction = result.scalars().first()

    if transaction:
        transaction.status = status
        if admin_id:
            transaction.admin_id = admin_id
        await session.commit()
        await session.refresh(transaction)

    return transaction


async def get_user_transactions(session: AsyncSession, user_id: int):
    """Get all transactions for a user"""
    stmt = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_pending_transactions(session: AsyncSession):
    """Get all pending transactions"""
    stmt = select(Transaction).where(Transaction.status == "pending").order_by(Transaction.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_transaction_by_id(session: AsyncSession, transaction_id: int):
    """Get transaction by ID"""
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await session.execute(stmt)
    return result.scalars().first()
