"""
Balance handlers - Top-up and payment confirmation
"""
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import text
from app.database import AsyncSessionLocal
from client_bot.config import logger
from client_bot.states import BalanceStates
from client_bot.utils.database import get_bot_info


def register_balance_handlers(dp, bot, owner_id: int, bot_token: str, bot_db_id: int):
    """Register balance related handlers"""

    @dp.message(Command("balance"))
    async def cmd_balance(message: Message):
        user_id = message.from_user.id

        async with AsyncSessionLocal() as session:
            query = text("SELECT balance FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
            result = await session.execute(query, {"user_id": user_id, "bot_id": bot_db_id})
            user = result.fetchone()

            if user:
                balance = float(user[0]) if user[0] else 0
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Hisobni to'ldirish", callback_data="topup_balance")]
                ])
                await message.answer(
                    f"Sizning hisobingiz: {balance:,.0f} so'm",
                    reply_markup=keyboard
                )
            else:
                await message.answer("Foydalanuvchi topilmadi. /start bosing.")

    @dp.callback_query(F.data == "topup_balance")
    async def topup_balance(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            "Hisobni to'ldirish\n\n"
            "Qancha summa to'ldirishni xohlaysiz?\n"
            "Misolda: 50000"
        )
        await state.set_state(BalanceStates.waiting_for_amount)
        await callback.answer()

    @dp.message(BalanceStates.waiting_for_amount)
    async def process_amount(message: Message, state: FSMContext):
        try:
            amount = float(message.text.replace(",", "").replace(" ", ""))
            if amount < 1000:
                await message.answer("Minimal summa: 1,000 so'm")
                return

            await state.update_data(amount=amount)

            # Get bot info for card number
            async with AsyncSessionLocal() as session:
                bot_info = await get_bot_info(session, bot_token)
                card_number = bot_info.get('card_number', 'N/A') if bot_info else 'N/A'

            await message.answer(
                f"To'lov ma'lumotlari:\n\n"
                f"Summa: {amount:,.0f} so'm\n"
                f"Karta raqam: <code>{card_number}</code>\n\n"
                f"To'lovni amalga oshirgandan keyin skrinshot yuboring.",
                parse_mode="HTML"
            )
            await state.set_state(BalanceStates.waiting_for_screenshot)

        except ValueError:
            await message.answer("Iltimos, to'g'ri summa kiriting (masalan: 50000)")

    @dp.message(BalanceStates.waiting_for_screenshot)
    async def process_screenshot(message: Message, state: FSMContext):
        if not message.photo:
            await message.answer("Iltimos, to'lov skrinshotini yuboring.")
            return

        user_data = await state.get_data()
        amount = user_data.get('amount')
        user_id = message.from_user.id
        username = message.from_user.username

        # Save transaction to database
        async with AsyncSessionLocal() as session:
            try:
                insert_query = text("""
                    INSERT INTO transactions (admin_id, user_id, username, amount, role, status)
                    VALUES (:admin_id, :user_id, :username, :amount, :role, :status)
                    RETURNING id
                """)
                result = await session.execute(insert_query, {
                    "admin_id": owner_id,
                    "user_id": user_id,
                    "username": username,
                    "amount": amount,
                    "role": "users_topup",
                    "status": "pending"
                })
                await session.commit()
                transaction_id = result.fetchone()[0]

                # Send to admin (bot owner)
                admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Tasdiqlash", callback_data=f"user_confirm_{transaction_id}"),
                        InlineKeyboardButton(text="Rad etish", callback_data=f"user_reject_{transaction_id}")
                    ]
                ])

                await bot.send_photo(
                    chat_id=owner_id,
                    photo=message.photo[-1].file_id,
                    caption=(
                        f"<b>Yangi to'lov so'rovi</b>\n\n"
                        f"Foydalanuvchi: @{username or 'N/A'} ({user_id})\n"
                        f"Summa: {amount:,.0f} so'm\n"
                        f"ID: #{transaction_id}"
                    ),
                    parse_mode="HTML",
                    reply_markup=admin_keyboard
                )

                await message.answer(
                    "To'lov so'rovi yuborildi!\n\n"
                    "Admin tasdiqlashini kuting."
                )
                await state.clear()

            except Exception as e:
                logger.error(f"Transaction save error: {e}")
                await message.answer("Xatolik yuz berdi. Qaytadan urinib ko'ring.")

    @dp.callback_query(F.data.startswith("user_confirm_"))
    async def admin_confirm_payment(callback: CallbackQuery):
        transaction_id = int(callback.data.split("_")[2])

        async with AsyncSessionLocal() as session:
            try:
                # Get transaction
                query = text("SELECT * FROM transactions WHERE id = :id")
                result = await session.execute(query, {"id": transaction_id})
                transaction = result.fetchone()

                if not transaction:
                    await callback.answer("Tranzaksiya topilmadi", show_alert=True)
                    return

                trans_dict = dict(transaction._mapping)
                user_id = trans_dict['user_id']
                amount = float(trans_dict['amount'])

                # Update transaction status
                update_query = text("UPDATE transactions SET status = 'approved' WHERE id = :id")
                await session.execute(update_query, {"id": transaction_id})

                # Update user balance (per-bot)
                balance_query = text("""
                    UPDATE users
                    SET balance = COALESCE(balance, 0) + :amount
                    WHERE user_id = :user_id AND bot_id = :bot_id
                """)
                await session.execute(balance_query, {"amount": amount, "user_id": user_id, "bot_id": bot_db_id})
                await session.commit()

                # Notify user
                try:
                    await bot.send_message(
                        user_id,
                        f"To'lovingiz tasdiqlandi!\n\n"
                        f"Summa: {amount:,.0f} so'm\n"
                        f"Hisobingiz to'ldirildi."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user: {e}")

                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n<b>TASDIQLANDI</b>",
                    parse_mode="HTML"
                )
                await callback.answer("To'lov tasdiqlandi")

            except Exception as e:
                logger.error(f"Confirmation error: {e}")
                await callback.answer("Xatolik yuz berdi", show_alert=True)

    @dp.callback_query(F.data.startswith("user_reject_"))
    async def admin_reject_payment(callback: CallbackQuery):
        transaction_id = int(callback.data.split("_")[2])

        async with AsyncSessionLocal() as session:
            try:
                # Get transaction
                query = text("SELECT * FROM transactions WHERE id = :id")
                result = await session.execute(query, {"id": transaction_id})
                transaction = result.fetchone()

                if not transaction:
                    await callback.answer("Tranzaksiya topilmadi", show_alert=True)
                    return

                trans_dict = dict(transaction._mapping)
                user_id = trans_dict['user_id']
                amount = float(trans_dict['amount'])

                # Update transaction status
                update_query = text("UPDATE transactions SET status = 'rejected' WHERE id = :id")
                await session.execute(update_query, {"id": transaction_id})
                await session.commit()

                # Notify user
                try:
                    await bot.send_message(
                        user_id,
                        f"To'lovingiz rad etildi.\n\n"
                        f"Summa: {amount:,.0f} so'm\n"
                        f"Iltimos, qayta urinib ko'ring yoki admin bilan bog'laning."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user: {e}")

                await callback.message.edit_caption(
                    caption=callback.message.caption + "\n\n<b>RAD ETILDI</b>",
                    parse_mode="HTML"
                )
                await callback.answer("To'lov rad etildi")

            except Exception as e:
                logger.error(f"Rejection error: {e}")
                await callback.answer("Xatolik yuz berdi", show_alert=True)
