from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.client_bot import ClientBot


async def create_client_bot(session: AsyncSession, user_id: int, bot_name: str, bot_token: str, **kwargs):
    """Create new client bot"""
    client_bot = ClientBot(
        user_id=user_id,
        bot_name=bot_name,
        bot_token=bot_token,
        **kwargs
    )
    session.add(client_bot)
    await session.commit()
    await session.refresh(client_bot)
    return client_bot


async def get_client_bots(session: AsyncSession, user_id: int):
    """Get all client bots"""
    stmt = select(ClientBot).where(ClientBot.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_bot_by_id(session: AsyncSession, bot_id: int):
    """Get bot by ID"""
    stmt = select(ClientBot).where(ClientBot.id == bot_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_bot_process_id(session: AsyncSession, bot_id: int, process_id: int):
    """Update bot process ID"""
    bot = await get_bot_by_id(session, bot_id)
    if bot:
        bot.process_id = process_id
        await session.commit()
        await session.refresh(bot)
    return bot


async def stop_client_bot(session: AsyncSession, bot_id: int):
    """Stop client bot - update status and return process_id for killing"""
    bot = await get_bot_by_id(session, bot_id)
    if bot:
        process_id = bot.process_id
        bot.status = "stopped"
        bot.process_id = None
        await session.commit()
        return process_id
    return None


async def get_bot_by_token(session: AsyncSession, bot_token: str):
    """Get bot by token"""
    stmt = select(ClientBot).where(ClientBot.bot_token == bot_token)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_bot_info(session: AsyncSession, bot_token: str, **kwargs):
    """Update bot info (bot_username, channel_username, manager_invite_link, etc)"""
    bot = await get_bot_by_token(session, bot_token)
    if bot:
        for key, value in kwargs.items():
            if hasattr(bot, key):
                setattr(bot, key, value)
        await session.commit()
        await session.refresh(bot)
    return bot


async def get_active_bot_by_owner(session: AsyncSession, owner_user_id: int):
    """
    Owner (client) ning faol botini olish (broadcast uchun).
    Agar bir nechta bot bo'lsa, birinchi faol botni qaytaradi.
    """
    stmt = select(ClientBot).where(
        ClientBot.user_id == owner_user_id,
        ClientBot.status == "active"
    )
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_all_active_bots_grouped_by_owner(session: AsyncSession):
    """
    Barcha faol botlarni owner bo'yicha olish.
    Returns: dict {owner_user_id: bot_token}
    """
    stmt = select(ClientBot.user_id, ClientBot.bot_token).where(
        ClientBot.status == "active"
    )
    result = await session.execute(stmt)

    # Har bir owner uchun birinchi faol botni olamiz
    bots_by_owner = {}
    for row in result.fetchall():
        owner_id = row[0]
        bot_token = row[1]
        if owner_id not in bots_by_owner:
            bots_by_owner[owner_id] = bot_token

    return bots_by_owner


async def set_bot_stop_flag(session: AsyncSession, bot_id: int, should_stop: bool = True):
    """
    Set bot stop flag in database.
    Bot will check this flag periodically and stop gracefully.
    """
    bot = await get_bot_by_id(session, bot_id)
    if bot:
        bot.should_stop = should_stop
        await session.commit()
        await session.refresh(bot)
    return bot


async def reset_bot_stop_flag(session: AsyncSession, bot_token: str):
    """
    Reset bot stop flag when bot starts.
    """
    bot = await get_bot_by_token(session, bot_token)
    if bot:
        bot.should_stop = False
        await session.commit()
        await session.refresh(bot)
    return bot


async def check_bot_should_stop(session: AsyncSession, bot_token: str) -> bool:
    """
    Check if bot should stop (called periodically by the bot).
    Returns True if bot should stop, False otherwise.
    """
    bot = await get_bot_by_token(session, bot_token)
    if bot:
        return bot.should_stop
    return False


async def set_bot_stop_flag_by_token(session: AsyncSession, bot_token: str, should_stop: bool = True):
    """
    Set bot stop flag by token.
    """
    bot = await get_bot_by_token(session, bot_token)
    if bot:
        bot.should_stop = should_stop
        await session.commit()
        await session.refresh(bot)
    return bot


async def get_bots_to_start(session: AsyncSession):
    """
    Ishga tushirish kerak bo'lgan botlarni olish.
    should_stop=False va (status='stopped' YOKI process_id=NULL) bo'lgan botlar.
    """
    from sqlalchemy import or_
    stmt = select(ClientBot).where(
        ClientBot.should_stop == False,
        or_(
            ClientBot.status.in_(["stopped", "free"]),
            ClientBot.process_id.is_(None)
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_bots_to_stop(session: AsyncSession):
    """
    To'xtatish kerak bo'lgan botlarni olish.
    should_stop=True va status='active' bo'lgan botlar.
    """
    stmt = select(ClientBot).where(
        ClientBot.should_stop == True,
        ClientBot.status == "active"
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_bot_status(session: AsyncSession, bot_id: int, status: str, process_id: int = None):
    """
    Bot statusini yangilash.
    """
    bot = await get_bot_by_id(session, bot_id)
    if bot:
        bot.status = status
        if process_id is not None:
            bot.process_id = process_id
        await session.commit()
        await session.refresh(bot)
    return bot


async def get_all_bots_for_monitoring(session: AsyncSession):
    """
    Monitoring uchun barcha botlarni olish.
    Returns: list of bots with their current state
    """
    stmt = select(ClientBot)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_bot_card_and_prices(
    session: AsyncSession,
    bot_id: int,
    card_number: str = None,
    oy_narx: float = None,
    yil_narx: float = None,
    cheksiz_narx: float = None
):
    """
    Bot karta raqami va narxlarini yangilash.
    Faqat berilgan qiymatlar yangilanadi.
    """
    bot = await get_bot_by_id(session, bot_id)
    if bot:
        if card_number is not None:
            bot.card_number = card_number
        if oy_narx is not None:
            bot.oy_narx = oy_narx
        if yil_narx is not None:
            bot.yil_narx = yil_narx
        if cheksiz_narx is not None:
            bot.cheksiz_narx = cheksiz_narx
        await session.commit()
        await session.refresh(bot)
    return bot
