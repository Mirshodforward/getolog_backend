import asyncio
import logging
import os
import subprocess
import sys
import psutil
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import text
from app.config import settings
from app.handlers import start_router, callback_router, message_router, balance_router
from app.database import init_db, check_db, AsyncSessionLocal
from app.crud.bot_crud import get_bots_to_start, update_bot_status, get_all_bots_for_monitoring

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if development mode (drop tables on startup for dev)
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


async def get_active_bots():
    """Get all active client bots from database"""
    async with AsyncSessionLocal() as session:
        query = text("""
            SELECT user_id, bot_token, bot_name
            FROM client_bots
            WHERE status = 'active'
            ORDER BY created_at
        """)
        result = await session.execute(query)
        bots = result.fetchall()
        return [dict(bot._mapping) for bot in bots]


def start_client_bot_process(bot_token: str, bot_name: str, owner_id: int) -> int:
    """Start a client bot in a subprocess. Returns process ID."""
    try:
        project_root = Path(__file__).resolve().parent
        client_bot_path = project_root / "client_bot_main.py"
        python_exe = sys.executable

        logger.info(f"🚀 Starting bot: {bot_name} (Owner: {owner_id})")

        # Log file for this bot
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in bot_name)
        log_file = logs_dir / f"bot_{safe_name}.log"
        log_handle = open(log_file, "a", encoding="utf-8")

        # Start subprocess
        process = subprocess.Popen(
            [python_exe, str(client_bot_path), bot_token, bot_name, str(owner_id)],
            stdout=log_handle,
            stderr=log_handle,
            stdin=subprocess.DEVNULL
        )
        logger.info(f"✅ Bot started: {bot_name} (PID: {process.pid}, Log: {log_file})")
        return process.pid
    except Exception as e:
        logger.error(f"❌ Failed to start bot {bot_name}: {e}")
        return None


async def start_all_client_bots():
    """Start all active client bots"""
    logger.info("🔍 Loading active client bots...")
    bots = await get_active_bots()

    if not bots:
        logger.info("📋 No active client bots found")
        return

    logger.info(f"📋 Found {len(bots)} active bot(s)")

    for bot in bots:
        pid = start_client_bot_process(
            bot_token=bot['bot_token'],
            bot_name=bot['bot_name'],
            owner_id=bot['user_id']
        )
        # Update process_id and status in database
        if pid:
            async with AsyncSessionLocal() as session:
                from app.crud.bot_crud import get_bot_by_token
                bot_record = await get_bot_by_token(session, bot['bot_token'])
                if bot_record:
                    bot_record.process_id = pid
                    bot_record.status = "active"
                    await session.commit()

    logger.info(f"✅ All {len(bots)} client bot(s) started")


def is_process_alive(pid: int) -> bool:
    """Check if process with given PID is still running"""
    if pid is None:
        return False
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def get_client_bot_processes() -> dict:
    """
    Barcha client_bot jarayonlarini topish.
    Returns: {bot_token: [list of PIDs]}
    """
    client_bots = {}

    try:
        for proc in psutil.process_iter(['pid', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) >= 4:
                    # client_bot_main.py <token> <name> <owner_id>
                    if 'client_bot_main.py' in str(cmdline):
                        bot_token = cmdline[2]  # Token 2-pozitsiyada
                        pid = proc.info['pid']
                        create_time = proc.info['create_time']

                        if bot_token not in client_bots:
                            client_bots[bot_token] = []
                        client_bots[bot_token].append({
                            'pid': pid,
                            'create_time': create_time
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
                continue
    except Exception as e:
        logger.error(f"Error scanning processes: {e}")

    return client_bots


async def process_cleaner_daemon():
    """
    Process cleaner daemon - har 10 sekundda duplicate jarayonlarni tozalaydi.

    Vazifalar:
    1. Har bir bot_token uchun faqat bitta jarayon qoldirish
    2. Bazadagi process_id bilan haqiqiy jarayonlarni solishtirish
    3. O'lik jarayonlarni bazadan tozalash
    """
    logger.info("🧹 Process cleaner daemon started")

    # Boshida 15 sekund kutish (botlar ishga tushishi uchun)
    await asyncio.sleep(15)

    while True:
        try:
            cleaned_count = 0

            # 1. Barcha client_bot jarayonlarini olish
            running_processes = get_client_bot_processes()

            # 2. Duplicate jarayonlarni tozalash
            for bot_token, processes in running_processes.items():
                if len(processes) > 1:
                    # Eng yangi jarayonni qoldirish, qolganlarini o'chirish
                    sorted_procs = sorted(processes, key=lambda x: x['create_time'], reverse=True)
                    newest_pid = sorted_procs[0]['pid']

                    for proc in sorted_procs[1:]:
                        try:
                            old_pid = proc['pid']
                            psutil.Process(old_pid).terminate()
                            logger.warning(f"🧹 Killed duplicate process: PID={old_pid} (keeping PID={newest_pid})")
                            cleaned_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

            # 3. Bazadagi process_id larni tekshirish
            async with AsyncSessionLocal() as session:
                all_bots = await get_all_bots_for_monitoring(session)

                for bot in all_bots:
                    if bot.process_id:
                        # Jarayon hali ishlayaptimi?
                        if not is_process_alive(bot.process_id):
                            logger.info(f"🔍 Dead process detected: {bot.bot_name} (PID={bot.process_id})")
                            bot.process_id = None
                            if bot.status == "active":
                                bot.status = "stopped"
                            await session.commit()
                            cleaned_count += 1
                        else:
                            # Jarayon ishlayapti, lekin bazadagi PID to'g'rimi?
                            bot_processes = running_processes.get(bot.bot_token, [])
                            active_pids = [p['pid'] for p in bot_processes]

                            if bot.process_id not in active_pids and active_pids:
                                # Bazadagi PID noto'g'ri, eng yangi PID ni saqlash
                                newest = max(bot_processes, key=lambda x: x['create_time'])
                                old_pid = bot.process_id
                                bot.process_id = newest['pid']
                                await session.commit()
                                logger.info(f"🔄 Updated PID: {bot.bot_name} ({old_pid} → {newest['pid']})")

            if cleaned_count > 0:
                logger.info(f"🧹 Process cleaner: {cleaned_count} jarayon tozalandi")

        except Exception as e:
            logger.error(f"❌ Process cleaner error: {e}")

        # 10 sekund kutish
        await asyncio.sleep(10)


def kill_old_process_if_running(bot_token: str, bot_name: str) -> bool:
    """
    Eski jarayonni tekshirish va o'chirish.
    Returns: True agar jarayon o'chirilgan bo'lsa, False aks holda
    """
    try:
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) >= 4:
                    if 'client_bot_main.py' in str(cmdline) and bot_token in str(cmdline):
                        pid = proc.info['pid']
                        logger.warning(f"🔪 Killing old process for {bot_name}: PID={pid}")
                        psutil.Process(pid).terminate()
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f"Error killing old process: {e}")
    return False


async def bot_monitor_daemon():
    """
    Bot monitor daemon - har 5 sekundda bazani tekshiradi.
    - should_stop=False va status=stopped → botni ishga tushirish
    - should_stop=True bo'lgan botlar o'zlari to'xtaydi (client_bot ichida)
    """
    logger.info("🔄 Bot monitor daemon started")

    # Boshida 20 sekund kutish (start_all_client_bots tugashi uchun)
    await asyncio.sleep(20)

    while True:
        try:
            async with AsyncSessionLocal() as session:
                # Ishga tushirish kerak bo'lgan botlarni olish
                bots_to_start = await get_bots_to_start(session)

                for bot in bots_to_start:
                    # 0. Shu token uchun allaqachon jarayon ishlayaptimi tekshirish
                    running_procs = get_client_bot_processes()
                    existing_procs = running_procs.get(bot.bot_token, [])
                    if existing_procs:
                        # Jarayon allaqachon ishlayapti — faqat bazani yangilash
                        newest = max(existing_procs, key=lambda x: x['create_time'])
                        bot.process_id = newest['pid']
                        bot.status = "active"
                        await session.commit()
                        logger.info(f"✅ Bot already running: {bot.bot_name} (PID={newest['pid']}), updated DB")
                        continue

                    # 1. Avval eski jarayonni tekshirish va o'chirish
                    if bot.process_id and is_process_alive(bot.process_id):
                        logger.warning(f"⚠️ Old process still running for {bot.bot_name} (PID={bot.process_id})")
                        try:
                            psutil.Process(bot.process_id).terminate()
                            logger.info(f"🔪 Terminated old process: PID={bot.process_id}")
                            await asyncio.sleep(1)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                    logger.info(f"🔄 Starting bot: {bot.bot_name} (should_stop=False, status={bot.status})")

                    # 2. Botni ishga tushirish
                    pid = start_client_bot_process(
                        bot_token=bot.bot_token,
                        bot_name=bot.bot_name,
                        owner_id=bot.user_id
                    )

                    if pid:
                        await update_bot_status(session, bot.id, "active", pid)
                        logger.info(f"✅ Bot started: {bot.bot_name} (PID: {pid})")
                    else:
                        logger.error(f"❌ Failed to start bot: {bot.bot_name}")

        except Exception as e:
            logger.error(f"❌ Bot monitor error: {e}")

        # 5 sekund kutish
        await asyncio.sleep(5)


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

    # Start process cleaner daemon as background task
    cleaner_task = asyncio.create_task(process_cleaner_daemon())
    logger.info("🧹 Process cleaner daemon ishga tushdi")

    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Include routers (order matters!)
    # MUHIM: start_router BIRINCHI bo'lishi kerak - /start komandasi har doim ishlashi uchun
    dp.include_router(start_router)
    dp.include_router(balance_router)
    dp.include_router(message_router)
    dp.include_router(callback_router)

    try:
        logger.info("🤖 Bot ishga tushdi...")
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Stop monitor daemon
        monitor_task.cancel()
        cleaner_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        try:
            await cleaner_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
