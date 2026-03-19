"""
Client Bot Main Entry Point
"""
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from client_bot.config import logger
from client_bot.handlers import register_all_handlers
from client_bot.utils.scheduler import scheduler
from client_bot.utils.database import get_bot_info
from app.database import AsyncSessionLocal
from app.crud import update_bot_info
from app.crud.bot_crud import check_bot_should_stop, reset_bot_stop_flag


async def check_stop_signal(bot_token: str, stop_event: asyncio.Event):
    """
    Periodically check database for stop signal.
    This runs as a background task and signals the bot to stop gracefully.
    """
    
    while not stop_event.is_set():
        try:
            async with AsyncSessionLocal() as session:
                should_stop = await check_bot_should_stop(session, bot_token)
                if should_stop:
                    logger.info(f"🛑 Stop signal received from admin panel for bot {bot_token[:10]}...!")
                    stop_event.set()
                    break
        except Exception as e:
            logger.error(f"Error checking stop signal: {e}")
        
        # Check every 5 seconds
        await asyncio.sleep(5)


async def save_bot_metadata(bot: Bot, bot_token: str, owner_id: int):
    """Save bot username and create manager invite link"""
    try:
        # Get bot username
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        logger.info(f"Bot username: @{bot_username}")

        # Get channel info from database
        async with AsyncSessionLocal() as session:
            db_bot_info = await get_bot_info(session, bot_token)
            if not db_bot_info:
                logger.warning("Bot info not found in database")
                return

            channel_id = db_bot_info.get('channel_id')
            if not channel_id:
                logger.warning("Channel ID not found")
                # Still save bot_username
                await update_bot_info(session, bot_token, bot_username=bot_username)
                return

        # Get channel info and create invite link
        channel_username = None
        manager_invite_link = None

        try:
            chat = await bot.get_chat(channel_id)
            channel_username = chat.username
            logger.info(f"Channel: @{channel_username or channel_id}")

            # Check if bot is admin in channel
            try:
                member = await bot.get_chat_member(channel_id, bot.session.bot_id)
                is_admin = member.status in ["administrator", "creator"]
                
                if not is_admin:
                    logger.warning(f"⚠️ Bot is NOT admin in channel {channel_id}!")
                    # Send warning to owner
                    try:
                        await bot.send_message(
                            owner_id,
                            f"⚠️ <b>MUHIM OGOHLANTIRISH!</b>\n\n"
                            f"🤖 Bot: {bot_username}\n"
                            f"📢 Kanal: {channel_username or channel_id}\n\n"
                            f"❌ Bot kanalda <b>ADMIN EMAS!</b>\n\n"
                            f"Bot to'g'ri ishlashi uchun uni kanalga admin sifatida qo'shing va /start ni qayta bosing.",
                            parse_mode="HTML"
                        )
                        logger.info(f"⚠️ Warning sent to owner {owner_id}")
                    except Exception as send_err:
                        logger.error(f"Could not send warning to owner: {send_err}")
                else:
                    logger.info(f"✅ Bot is admin in channel {channel_id}")
            except Exception as admin_check_err:
                logger.warning(f"Could not check admin status: {admin_check_err}")

            # Create permanent invite link for manager (never expires, unlimited uses)
            invite = await bot.create_chat_invite_link(
                channel_id,
                name="Manager Access",
                creates_join_request=False
            )
            manager_invite_link = invite.invite_link
            logger.info(f"Manager invite link created: {manager_invite_link}")

        except Exception as e:
            logger.error(f"Error getting channel info: {e}")

        # Save to database
        async with AsyncSessionLocal() as session:
            await update_bot_info(
                session,
                bot_token,
                bot_username=bot_username,
                channel_username=channel_username,
                manager_invite_link=manager_invite_link
            )
            logger.info("Bot metadata saved to database")

    except Exception as e:
        logger.error(f"Error saving bot metadata: {e}")


async def start_client_bot(bot_token: str, bot_username: str, owner_id: int):
    """
    Client bot ni ishga tushirish

    Args:
        bot_token: Telegram bot token
        bot_username: Bot nomi
        owner_id: Bot egasining telegram ID (admin_id sifatida ishlatiladi)
    """
    stop_event = asyncio.Event()
    
    try:
        logger.info(f"Client bot ishga tushurilmoqda...")
        logger.info(f"Bot nomi: {bot_username}")
        logger.info(f"Owner ID: {owner_id}")
        logger.info(f"Token: {bot_token[:20]}...")

        # Reset stop flag when starting
        async with AsyncSessionLocal() as session:
            await reset_bot_stop_flag(session, bot_token)
            logger.info("✅ Stop flag reset")

        # Bot instance yaratish
        bot = Bot(token=bot_token)
        dp = Dispatcher(storage=MemoryStorage())

        # Bot info test
        try:
            bot_info = await bot.get_me()
            logger.info(f"Bot authenticated: @{bot_info.username}")
        except Exception as e:
            logger.error(f"Bot authentication failed: {e}")
            return

        # Save bot metadata (username, channel info, invite link)
        await save_bot_metadata(bot, bot_token, owner_id)

        # Get bot_db_id from database for per-bot user tracking
        bot_db_id = None
        async with AsyncSessionLocal() as session:
            db_bot_info = await get_bot_info(session, bot_token)
            if db_bot_info:
                bot_db_id = db_bot_info['id']
                logger.info(f"Bot DB ID: {bot_db_id}")
            else:
                logger.warning("Bot info not found in database!")

        # Register all handlers
        register_all_handlers(dp, bot, owner_id, bot_username, bot_token, bot_db_id)
        logger.info("All handlers registered")

        logger.info(f"Bot '{bot_username}' ready for polling...")

        # Start scheduler natively if not already running
        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler started")
        else:
            logger.info("Scheduler already running, reusing")

        # Start stop signal checker as background task
        stop_checker_task = asyncio.create_task(check_stop_signal(bot_token, stop_event))
        logger.info("🔍 Stop signal checker started")

        # Custom polling loop with stop signal support
        async def custom_polling():
            """Custom polling that can be stopped gracefully and resumes on temporary errors"""
            while not stop_event.is_set():
                try:
                    await dp.start_polling(
                        bot,
                        allowed_updates=dp.resolve_used_update_types(),
                        handle_signals=False  # We handle signals manually
                    )
                    # If start_polling stops on its own naturally:
                    break
                except asyncio.CancelledError:
                    logger.info("Polling cancelled")
                    break
                except Exception as loop_e:
                    logger.error(f"Polling crashed: {loop_e}. Retrying in 5 seconds...", exc_info=True)
                    if stop_event.is_set():
                        break
                    await asyncio.sleep(5)

        # Start polling task
        polling_task = asyncio.create_task(custom_polling())
        
        # Wait for either stop signal or polling to finish
        done, pending = await asyncio.wait(
            [polling_task, stop_checker_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Stop the dispatcher
        await dp.stop_polling()
        logger.info("🛑 Bot polling stopped")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Warning: do NOT shutdown the global scheduler here if in multi-bot mode
        logger.info(f"Bot session cleanup for {bot_token[:10]}...")
        
        if 'bot' in locals():
            await bot.session.close()
            logger.info("Bot session closed")
        
        # Update status in database
        # MUHIM: should_stop ni o'zgartirmaymiz - admin panel boshqaradi
        try:
            async with AsyncSessionLocal() as session:
                from app.crud.bot_crud import get_bot_by_token
                bot_record = await get_bot_by_token(session, bot_token)
                if bot_record:
                    bot_record.status = "stopped"
                    bot_record.process_id = None
                    # should_stop ni o'zgartirmaymiz - daemon qayta ishga tushirmasligi uchun
                    await session.commit()
                    logger.info("✅ Bot status updated to 'stopped' in database")
        except Exception as db_error:
            logger.error(f"Error updating bot status: {db_error}")
        
        logger.info(f"🏁 Bot '{bot_username}' fully stopped")


def run_bot(bot_token: str, bot_username: str, owner_id: int):
    """Run the bot (blocking call)"""
    logger.info("=" * 50)
    logger.info("CLIENT BOT STARTED")
    logger.info("=" * 50)

    try:
        asyncio.run(start_client_bot(bot_token, bot_username, owner_id))
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        logger.error("Ishlatilish: python -m client_bot.main <bot_token> <bot_username> <owner_id>")
        sys.exit(1)

    bot_token = sys.argv[1]
    bot_username = sys.argv[2]
    owner_id = int(sys.argv[3])

    run_bot(bot_token, bot_username, owner_id)
