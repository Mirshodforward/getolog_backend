"""
Plan purchase handlers - Monthly, Yearly, Unlimited plans
"""
from aiogram import F
from aiogram.types import CallbackQuery
from sqlalchemy import text
from decimal import Decimal
from app.database import AsyncSessionLocal
from app.crud.spending_crud import create_user_spending
from client_bot.config import logger
from client_bot.utils.database import get_bot_info
from client_bot.utils.scheduler import schedule_kick


def register_plan_handlers(dp, bot, owner_id: int, bot_token: str, bot_db_id: int):
    """Register plan purchase handlers"""

    @dp.callback_query(F.data == "plan_test_2min")
    async def purchase_test_plan(callback: CallbackQuery):
        user_id = callback.from_user.id
        username = callback.from_user.username
        user_name = callback.from_user.full_name or "User"

        async with AsyncSessionLocal() as session:
            try:
                # Get bot info for channel_id
                bot_info = await get_bot_info(session, bot_token)
                if not bot_info:
                    await callback.answer("Bot ma'lumotlari topilmadi", show_alert=True)
                    return

                channel_id = bot_info.get('channel_id')

                if not channel_id:
                    await callback.answer("Kanal ID topilmadi", show_alert=True)
                    return

                # Get user info (per-bot)
                query = text("SELECT name FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
                result = await session.execute(query, {"user_id": user_id, "bot_id": bot_db_id})
                user = result.fetchone()

                stored_name = user[0] if user and user[0] else user_name

                # Create invite link for channel
                try:
                    invite = await bot.create_chat_invite_link(
                        channel_id,
                        member_limit=1
                    )
                    invite_link = invite.invite_link
                except Exception as e:
                    logger.error(f"Invite link yaratishda xato: {e}")
                    await callback.answer("Kanal linkini yaratib bo'lmadi", show_alert=True)
                    return

                # Fetch existing end date to stack 2 min
                check_q = text("SELECT plan_start_date, plan_end_date FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
                res = await session.execute(check_q, {"user_id": user_id, "bot_id": bot_db_id})
                u_row = res.fetchone()

                import pytz
                from client_bot.config import TIMEZONE
                from datetime import datetime as dt
                from datetime import timedelta
                now = dt.now(TIMEZONE)

                base_date = now
                start_date = now
                if u_row and u_row[1]:
                    ex_end = u_row[1]
                    if ex_end.tzinfo is None:
                        ex_end = pytz.UTC.localize(ex_end)
                    if ex_end > now:
                        base_date = ex_end
                        start_date = u_row[0] if u_row[0] else now

                end_date = base_date + timedelta(minutes=2)

                # Update user with test duration (per-bot)
                update_user = text("""
                    UPDATE users
                    SET duration = :duration,
                        status = :status,
                        invite_link = :invite_link,
                        plan_start_date = :start_date,
                        plan_end_date = :end_date
                    WHERE user_id = :user_id AND bot_id = :bot_id
                """)
                await session.execute(update_user, {
                    "duration": "2 daqiqa",
                    "status": "active",
                    "invite_link": invite_link,
                    "user_id": user_id,
                    "bot_id": bot_db_id,
                    "start_date": start_date,
                    "end_date": end_date
                })
                await session.commit()

                # Notify user with invite link
                await callback.message.edit_text(
                    f"<b>Test rejim faollashtirildi!</b>\n\n"
                    f"2 daqiqalik test\n"
                    f"Summa: Bepul\n\n"
                    f"Kanalga qo'shilish linki:\n{invite_link}\n\n"
                    f"Muddat: 2 daqiqa",
                    parse_mode="HTML"
                )

                # Notify bot owner (client) about new test member
                try:
                    await bot.send_message(
                        owner_id,
                        f"<b>Test a'zo qo'shildi!</b>\n\n"
                        f"User: {stored_name}\n"
                        f"Username: @{username or 'N/A'}\n"
                        f"User ID: {user_id}\n"
                        f"Muddat: 2 daqiqa (Test)\n"
                        f"Summa: Bepul",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify owner: {e}")

                # Schedule kick after 2 minutes
                await schedule_kick(bot, channel_id, user_id, owner_id, "2 daqiqa", bot_db_id)

                await callback.answer("Test rejim faollashtirildi!")

            except Exception as e:
                logger.error(f"Test plan error: {e}")
                await callback.answer("Xatolik yuz berdi", show_alert=True)

    @dp.callback_query(F.data == "plan_monthly")
    async def purchase_monthly_plan(callback: CallbackQuery):
        await purchase_plan(callback, bot, owner_id, "monthly", bot_token, bot_db_id)

    @dp.callback_query(F.data == "plan_yearly")
    async def purchase_yearly_plan(callback: CallbackQuery):
        await purchase_plan(callback, bot, owner_id, "yearly", bot_token, bot_db_id)

    @dp.callback_query(F.data == "plan_unlimited")
    async def purchase_unlimited_plan(callback: CallbackQuery):
        await purchase_plan(callback, bot, owner_id, "unlimited", bot_token, bot_db_id)


async def purchase_plan(callback: CallbackQuery, bot, owner_id: int, plan_type: str, bot_token: str, bot_db_id: int):
    """Generic plan purchase handler"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    user_name = callback.from_user.full_name or "User"

    # Plan configurations
    plan_config = {
        "monthly": {"price_field": "oy_narx", "duration": "1 oy", "label": "Oylik"},
        "yearly": {"price_field": "yil_narx", "duration": "1 yil", "label": "Yillik"},
        "unlimited": {"price_field": "cheksiz_narx", "duration": "cheksiz", "label": "Cheksiz"}
    }

    config = plan_config.get(plan_type)
    if not config:
        await callback.answer("Noto'g'ri tarif", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        try:
            # Get bot info for price and channel_id
            bot_info = await get_bot_info(session, bot_token)
            if not bot_info or not bot_info.get(config["price_field"]):
                await callback.answer("Narx topilmadi", show_alert=True)
                return

            price = float(bot_info[config["price_field"]])
            channel_id = bot_info.get('channel_id')

            if not channel_id:
                await callback.answer("Kanal ID topilmadi", show_alert=True)
                return

            # Check user balance (per-bot)
            query = text("SELECT balance, name FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
            result = await session.execute(query, {"user_id": user_id, "bot_id": bot_db_id})
            user = result.fetchone()

            if not user:
                await callback.answer("Foydalanuvchi topilmadi", show_alert=True)
                return

            balance = float(user[0]) if user[0] else 0
            stored_name = user[1] or user_name

            if balance < price:
                await callback.answer(
                    f"Hisobingizda yetarli mablag' yo'q!\n\n"
                    f"Kerak: {price:,.0f} so'm\n"
                    f"Mavjud: {balance:,.0f} so'm",
                    show_alert=True
                )
                return

            # Create invite link for channel
            try:
                invite = await bot.create_chat_invite_link(
                    channel_id,
                    member_limit=1
                )
                invite_link = invite.invite_link
            except Exception as e:
                logger.error(f"Invite link yaratishda xato: {e}")
                await callback.answer("Kanal linkini yaratib bo'lmadi", show_alert=True)
                return

            # Fetch existing end date for stacking subscriptions
            check_q = text("SELECT plan_start_date, plan_end_date FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
            res = await session.execute(check_q, {"user_id": user_id, "bot_id": bot_db_id})
            usr_data = res.fetchone()

            import pytz
            from client_bot.config import TIMEZONE
            from datetime import timedelta
            from datetime import datetime as dt
            
            now = dt.now(TIMEZONE)
            base_date = now
            start_date = now
            if usr_data and usr_data[1]:
                ex_end = usr_data[1]
                if ex_end.tzinfo is None:
                    ex_end = pytz.UTC.localize(ex_end)
                if ex_end > now:
                    base_date = ex_end
                    start_date = usr_data[0] if usr_data[0] else now

            duration_str = config["duration"].lower()
            if "2 daqiqa" in duration_str:
                end_date = base_date + timedelta(minutes=2)
            elif "oy" in duration_str or "oylik" in duration_str:
                end_date = base_date + timedelta(days=30)
            elif "yil" in duration_str or "yillik" in duration_str:
                end_date = base_date + timedelta(days=365)
            elif "cheksiz" in duration_str:
                end_date = None
            else:
                end_date = base_date + timedelta(days=30)

            # Deduct from balance and update duration, invite_link (per-bot)
            update_balance = text("""
                UPDATE users
                SET balance = balance - :price,
                    duration = :duration,
                    status = :status,
                    invite_link = :invite_link,
                    plan_start_date = :start_date,
                    plan_end_date = :end_date
                WHERE user_id = :user_id AND bot_id = :bot_id
            """)
            await session.execute(update_balance, {
                "price": price,
                "duration": config["duration"],
                "status": "active",
                "invite_link": invite_link,
                "user_id": user_id,
                "bot_id": bot_db_id,
                "start_date": start_date,
                "end_date": end_date
            })

            # Create transaction
            insert_transaction = text("""
                INSERT INTO transactions (admin_id, user_id, username, amount, role, status)
                VALUES (:admin_id, :user_id, :username, :amount, :role, :status)
                RETURNING id
            """)
            result = await session.execute(insert_transaction, {
                "admin_id": owner_id,
                "user_id": user_id,
                "username": username,
                "amount": price,
                "role": "plan_purchase",
                "status": "approved"
            })
            transaction_id = result.fetchone()[0]

            # Create spending record for user
            await create_user_spending(
                session=session,
                user_id=user_id,
                amount=Decimal(str(price)),
                spend=config["duration"],  # "1 oy", "1 yil", "cheksiz"
                admin_id=owner_id,
                bot_username=bot_info.get('bot_username'),
                username=username
            )

            await session.commit()

            # Notify user with invite link
            await callback.message.edit_text(
                f"<b>Muvaffaqiyatli!</b>\n\n"
                f"{config['label']} tarif sotib olindi\n"
                f"Summa: {price:,.0f} so'm\n"
                f"Yangi balans: {balance - price:,.0f} so'm\n\n"
                f"Kanalga qo'shilish linki:\n{invite_link}\n\n"
                f"Muddat: {config['duration'].capitalize()}",
                parse_mode="HTML"
            )

            # Notify bot owner (client) about new member
            try:
                await bot.send_message(
                    owner_id,
                    f"<b>Yangi a'zo qo'shildi!</b>\n\n"
                    f"User: {stored_name}\n"
                    f"Username: @{username or 'N/A'}\n"
                    f"User ID: {user_id}\n"
                    f"Muddat: {config['duration'].capitalize()}\n"
                    f"Summa: {price:,.0f} so'm\n"
                    f"Transaction ID: #{transaction_id}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify owner: {e}")

            # Schedule kick (will be skipped for unlimited)
            await schedule_kick(bot, channel_id, user_id, owner_id, config["duration"], bot_db_id)

            await callback.answer("Tarif faollashtirildi!")

        except Exception as e:
            logger.error(f"Plan purchase error: {e}")
            await callback.answer("Xatolik yuz berdi", show_alert=True)
