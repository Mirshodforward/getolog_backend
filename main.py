import asyncio
import logging
import os
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import text
from app.config import settings
from app.handlers import start_router, callback_router, message_router, balance_router, renew_plan_router
from app.database import init_db, check_db, AsyncSessionLocal
from app.crud.bot_crud import get_bots_to_start, update_bot_status, get_all_bots_for_monitoring
from app.models.client import Client
from sqlalchemy import select
from app.crud.spending_crud import create_client_spending
from app.config import PLAN_CONFIG
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if development mode (drop tables on startup for dev)
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


async def get_active_bots():
    """Get all active client bots from database"""
    async with AsyncSessionLocal() as session:
        query = text("""
            SELECT user_id, bot_token, bot_username
            FROM client_bots
            WHERE status = 'active'
            ORDER BY created_at
        """)
        result = await session.execute(query)
        bots = result.fetchall()
        return [dict(bot._mapping) for bot in bots]

async def start_all_client_bots():
    """Start all active client bots"""
    logger.info("🔍 Loading active client bots...")
    bots = await get_active_bots()

    if not bots:
        logger.info("📋 No active client bots found")
        return

    from app.bot_manager import run_bot_in_background
    logger.info(f"📋 Found {len(bots)} active bot(s)")

    for bot in bots:
        await run_bot_in_background(
            bot_token=bot['bot_token'],
            bot_username=bot['bot_username'],
            owner_id=bot['user_id']
        )

    logger.info(f"✅ All {len(bots)} client bot(s) started")


async def bot_monitor_daemon():
    """
    Bot monitor daemon - har 5 sekundda bazani tekshiradi.
    - should_stop=False va status=stopped → botni ishga tushirish
    - status=active bolib lekin task larda yoq bolgan botlarni ishga tushiradi
    """
    logger.info("🔄 Bot monitor daemon started")
    from app.bot_manager import run_bot_in_background, is_bot_running

    # Boshida 20 sekund kutish (start_all_client_bots tugashi uchun)
    await asyncio.sleep(20)

    while True:
        try:
            async with AsyncSessionLocal() as session:
                # Barcha kerakli botlarni olamiz (status=active yoki (status=stopped va should_stop=False))
                query = text("SELECT id, user_id, bot_token, bot_username, status FROM client_bots WHERE status = 'active' OR (status = 'stopped' AND should_stop = FALSE)")
                result = await session.execute(query)
                all_needed_bots = result.fetchall()

                # Get missing tokens and start them
                for bot in all_needed_bots:
                    if not is_bot_running(bot.bot_token):
                        logger.info(f"🔄 Starting bot (was not running): {bot.bot_username}")
                        await run_bot_in_background(
                            bot_token=bot.bot_token,
                            bot_username=bot.bot_username,
                            owner_id=bot.user_id
                        )
                        # Agar status=stopped bolsa active qilamiz
                        if bot.status != "active":
                            await update_bot_status(session, bot.id, "active", None)
                            logger.info(f"✅ Bot status updated to active: {bot.bot_username}")

        except Exception as e:
            logger.error(f"❌ Bot monitor error: {e}")

        # 5 sekund kutish
        await asyncio.sleep(5)


async def plan_monitor_daemon(bot: Bot):
    """
    Mijozlarning tarif muddatlarini tekshirish darmoni.
    - Agar tarif tugashiga 1 kun qolgan bo'lsa va balansida yetarli mablag' bo'lsa, avto-yangilaydi.
    - Agar muddat tugagan bo'lsa va mablag' yetarli bo'lmasa, uni "free" tarifiga tushiradi.
    """
    logger.info("📅 Plan monitor daemon started")
    
    # Boshida 30 sekund kutish
    await asyncio.sleep(30)
    
    while True:
        try:
            async with AsyncSessionLocal() as session:
                # Faqat 'free' emas bo'lgan, end_date bor mijozlarni olamiz
                stmt = select(Client).where(Client.plan_type.in_(["standard", "standart", "biznes"]), Client.plan_end_date.isnot(None))
                result = await session.execute(stmt)
                clients = result.scalars().all()
                
                now_tz = datetime.datetime.now(datetime.timezone.utc)
                
                for client in clients:
                    end_date = client.plan_end_date
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=datetime.timezone.utc)
                    
                    time_left = end_date - now_tz
                    
                    # Agar muddati o'tgan bo'lsa yoki 1 kundan kam vaqt qolgan bo'lsa
                    if time_left.total_seconds() <= 86400: # 24 soat
                        plan_name = client.plan_type
                        if plan_name not in PLAN_CONFIG:
                            continue
                            
                        price = PLAN_CONFIG[plan_name]["price"]
                        current_balance = float(client.balance) if client.balance else 0
                        
                        # Balans yetarlimi va Avto-to'lov yonig'mi?
                        if current_balance >= price and client.oylik_obuna:
                            # Pulni yechish va 30 kunga uzaytirish
                            client.balance -= price
                            
                            # Spending yozuvini qo'shish
                            await create_client_spending(
                                session=session,
                                user_id=client.user_id,
                                amount=price,
                                spend=f"Avto-yangilash: {plan_name.capitalize()}",
                                username=client.username
                            )
                            
                            # Agar u allaqachon tugagan bo'lsa hozirdan boshlab hisoblaymiz, 
                            # agar hali vaqti bo'lsa, eski muddatiga 30 kun qo'shamiz
                            if time_left.total_seconds() <= 0:
                                client.plan_start_date = now_tz
                                client.plan_end_date = now_tz + datetime.timedelta(days=30)
                            else:
                                client.plan_end_date = end_date + datetime.timedelta(days=30)
                                
                            await session.commit()
                            
                            try:
                                await bot.send_message(
                                    client.user_id,
                                    f"✅ <b>Tarifingiz avtomatik tarzda uzaytirildi!</b>\n\n"
                                    f"💎 Tarif: {plan_name.capitalize()}\n"
                                    f"💸 Yechildi: {price:,.0f} so'm\n"
                                    f"📅 Yangi muddat: {client.plan_end_date.strftime('%d.%m.%Y %H:%M')}\n",
                                    parse_mode="HTML"
                                )
                            except Exception as e:
                                logger.error(f"Cannot send welcome message to {client.user_id}: {e}")
                                
                        else:
                            # Mablag' yetarli emas yoki Avto-to'lov o'chiq. Agar muddati aniq o'tib bo'lgan bo'lsa -> free ga tushiramiz
                            if time_left.total_seconds() <= 0:
                                client.plan_type = "free"
                                client.plan_start_date = None
                                client.plan_end_date = None
                                await session.commit()
                                
                                try:
                                    reason = "Avto-to'lov o'chirilganligi sababli" if not client.oylik_obuna else "Hisobingizda mablag' yetarli bo'lmaganligi sababli"
                                    await bot.send_message(
                                        client.user_id,
                                        f"⚠️ <b>Tarifingiz muddati tugadi!</b>\n\n"
                                        f"{reason} tarifingiz avtomatik uzaytirilmadi.\n"
                                        f"Hozirda sizning tarifingiz <b>Free</b> ga o'zgartirildi.\n\n"
                                        f"Qayta faollashtirish uchun balansingizni to'ldirib, tarifni yangilang.",
                                        parse_mode="HTML"
                                    )
                                except Exception as e:
                                    pass
                            
        except Exception as e:
            logger.error(f"❌ Plan monitor error: {e}")

        # Har 15 daqiqada bir tekshiradi
        await asyncio.sleep(900)


async def main():
    """Main function"""
    # Check and initialize database
    db_available = await check_db()
    if not db_available:
        logger.error("❌ Database ulanish olmadi!")
        return

    # Create tables (drop existing only in dev mode)
    await init_db(drop_all=DEV_MODE)

    # Start all active client bots
    await start_all_client_bots()

    # Start bot monitor daemon as background task
    monitor_task = asyncio.create_task(bot_monitor_daemon())
    logger.info("🔄 Bot monitor daemon ishga tushdi")

    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Start plan monitor daemon as background task
    plan_task = asyncio.create_task(plan_monitor_daemon(bot))
    logger.info("📅 Plan monitor daemon ishga tushdi")

    # Include routers (order matters!)
    # MUHIM: start_router BIRINCHI bo'lishi kerak - /start komandasi har doim ishlashi uchun
    dp.include_router(start_router)
    dp.include_router(balance_router)
    dp.include_router(message_router)
    dp.include_router(callback_router)
    dp.include_router(renew_plan_router)

    try:
        logger.info("🤖 Bot ishga tushdi...")
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Stop monitor daemon
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
