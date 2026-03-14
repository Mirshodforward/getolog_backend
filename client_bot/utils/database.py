"""
Database helper functions for Client Bot
"""
from sqlalchemy import text
from app.database import AsyncSessionLocal
from client_bot.config import logger


async def get_or_create_user(
    session,
    admin_id: int,
    user_id: int,
    bot_id: int,
    username: str = None,
    name: str = None
):
    """Get or create user in users table (per-bot)"""
    # Check if user exists for this specific bot
    query = text("SELECT * FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
    result = await session.execute(query, {"user_id": user_id, "bot_id": bot_id})
    user = result.fetchone()

    if user:
        return dict(user._mapping)

    # Create new user for this bot
    insert_query = text("""
        INSERT INTO users (admin_id, user_id, bot_id, username, name, terms, language)
        VALUES (:admin_id, :user_id, :bot_id, :username, :name, :terms, :language)
        RETURNING *
    """)

    result = await session.execute(insert_query, {
        "admin_id": admin_id,
        "user_id": user_id,
        "bot_id": bot_id,
        "username": username,
        "name": name,
        "terms": True,
        "language": "uz"
    })

    await session.commit()
    user = result.fetchone()

    return dict(user._mapping) if user else None


async def get_bot_info(session, bot_token: str):
    """Get bot information from client_bots table by bot_token"""
    query = text("SELECT * FROM client_bots WHERE bot_token = :bot_token")
    result = await session.execute(query, {"bot_token": bot_token})
    bot_info = result.fetchone()

    return dict(bot_info._mapping) if bot_info else None


async def get_client_plan(session, owner_id: int):
    """Get client plan type from clients table"""
    query = text("SELECT plan_type FROM clients WHERE user_id = :user_id")
    result = await session.execute(query, {"user_id": owner_id})
    client = result.fetchone()

    if client:
        return client[0] or 'free'
    return 'free'


async def get_client_language(session, owner_id: int) -> str:
    """Get client language from clients table"""
    query = text("SELECT language FROM clients WHERE user_id = :user_id")
    result = await session.execute(query, {"user_id": owner_id})
    client = result.fetchone()

    if client and client[0]:
        return client[0]
    return 'uz'
