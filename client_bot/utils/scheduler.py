"""
Scheduler functions for auto-kick feature
"""
from datetime import datetime, timedelta
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import AsyncSessionLocal
from client_bot.config import logger, TIMEZONE

# Global scheduler
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def kick_user_from_channel(bot, channel_id: int, user_id: int, owner_id: int, bot_id: int):
    """Kick user from channel after duration expires"""
    logger.info(f"Vaqt tugadi! User {user_id} chiqarilmoqda (bot_id={bot_id})...")

    user_info = None
    invite_link = None
    duration = None

    # Get user info from database (per-bot)
    async with AsyncSessionLocal() as session:
        query = text("SELECT * FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
        result = await session.execute(query, {"user_id": user_id, "bot_id": bot_id})
        user = result.fetchone()

        if user:
            user_dict = dict(user._mapping)
            user_info = user_dict.get('name')
            invite_link = user_dict.get('invite_link')
            duration = user_dict.get('duration')

            # Update status to removed (per-bot)
            update_query = text("UPDATE users SET status = 'removed' WHERE user_id = :user_id AND bot_id = :bot_id")
            await session.execute(update_query, {"user_id": user_id, "bot_id": bot_id})
            await session.commit()

    # Revoke invite link
    if invite_link:
        try:
            await bot.revoke_chat_invite_link(channel_id, invite_link)
            logger.info(f"User {user_id} ning linki revoke qilindi")
        except Exception as e:
            logger.error(f"Link revoke qilishda xato: {e}")

    # Kick user from channel (ban + unban)
    try:
        await bot.ban_chat_member(channel_id, user_id)
        await bot.unban_chat_member(channel_id, user_id)
        logger.info(f"User {user_id} kanaldan chiqarildi")
    except Exception as e:
        logger.error(f"Kanaldan chiqarishda xato: {e}")

    # Notify user
    try:
        await bot.send_message(
            user_id,
            f"Muddatingiz tugadi!\n\n"
            f"Siz kanaldan chiqarib yuborildingiz.\n"
            f"Qayta qo'shilish uchun /start bosing."
        )
    except Exception as e:
        logger.error(f"Userga xabar yuborishda xato: {e}")

    # Notify owner (admin/client)
    try:
        await bot.send_message(
            owner_id,
            f"<b>Muddat tugadi</b>\n\n"
            f"User: {user_info or 'N/A'} ({user_id})\n"
            f"Muddat: {duration}\n"
            f"Kanaldan chiqarildi.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ownerga xabar yuborishda xato: {e}")


async def schedule_kick(bot, channel_id: int, user_id: int, owner_id: int, duration: str, bot_id: int):
    """Schedule user kick based on duration"""
    # Parse duration string to minutes
    duration_minutes = 0
    if "2 daqiqa" in duration:
        duration_minutes = 2  # 2 minutes for testing
    elif "1 oy" in duration or "oylik" in duration.lower():
        duration_minutes = 30 * 24 * 60  # 30 days
    elif "1 yil" in duration or "yillik" in duration.lower():
        duration_minutes = 365 * 24 * 60  # 365 days
    elif "cheksiz" in duration.lower() or "unlimited" in duration.lower():
        # Cheksiz uchun schedule qilmaymiz
        logger.info(f"User {user_id} cheksiz muddat oldi, schedule qilinmaydi")
        return
    else:
        logger.warning(f"Noma'lum duration: {duration}")
        return

    # Calculate run time
    current_time = datetime.now(TIMEZONE)
    run_time = current_time + timedelta(minutes=duration_minutes)

    logger.info(f"User {user_id} uchun chiqarish: {run_time.strftime('%Y-%m-%d %H:%M:%S')} ({duration})")

    # Add job to scheduler
    scheduler.add_job(
        kick_user_from_channel,
        trigger="date",
        run_date=run_time,
        args=[bot, channel_id, user_id, owner_id, bot_id],
        id=f"kick_{bot_id}_{user_id}_{run_time.timestamp()}"
    )
