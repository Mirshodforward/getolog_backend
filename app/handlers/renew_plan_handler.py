import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.crud import get_client_by_user_id
from app.config import PLAN_CONFIG
from app.translations import get_text as _
import app.crud.spending_crud as spending_crud

router = Router()

@router.callback_query(F.data == "buy_plan")
async def show_renew_plans(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if not client:
            return await callback.answer("Client not found", show_alert=True)
        
        lang = client.language or "uz"
        current_balance = float(client.balance) if client.balance else 0

    topup_text = {
        "uz": "💳 Balansni to'ldirish", 
        "ru": "💳 Пополнить баланс", 
        "en": "💳 Top up balance"
    }

    back_text = {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} so'm) - 1 oy", callback_data="renew_plan_standard")],
        [InlineKeyboardButton(text=f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} so'm) - 1 oy", callback_data="renew_plan_biznes")],
        [InlineKeyboardButton(text=topup_text.get(lang, topup_text["uz"]), callback_data="topup_balance")],
        [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="back_to_main")]
    ])
    
    texts = {
        "uz": f"💰 <b>Tarifni yangilash / Sotib olish</b>\n\nSizning balansingiz: <b>{current_balance:,.0f} so'm</b>\nKerakli tarifni tanlang:",
        "ru": f"💰 <b>Обновить / Купить тариф</b>\n\nВаш баланс: <b>{current_balance:,.0f} сум</b>\nВыберите тариф:",
        "en": f"💰 <b>Renew / Buy Plan</b>\n\nYour balance: <b>{current_balance:,.0f} UZS</b>\nSelect a plan:"
    }
    
    await callback.message.edit_text(texts.get(lang, texts["uz"]), reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

async def process_renewal(callback: CallbackQuery, plan_name: str):
    user_id = callback.from_user.id
    plan_price = PLAN_CONFIG[plan_name]["price"]
    
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if not client:
            return await callback.answer("Client not found", show_alert=True)
            
        lang = client.language or "uz"
        current_balance = float(client.balance) if client.balance else 0
        
        if current_balance < plan_price:
            needed = plan_price - current_balance
            msg = {
                "uz": f"⚠️ <b>Hisobingizda yetarli mablag' yo'q!</b>\nKerakli: <b>{plan_price:,} so'm</b>\nYana <b>{needed:,.0f} so'm</b> kerak.\nIltimos, balansingizni to'ldiring.",
                "ru": f"⚠️ <b>Недостаточно средств!</b>\nНужно: <b>{plan_price:,} сум</b>\nНе хватает <b>{needed:,.0f} сум</b>.",
                "en": f"⚠️ <b>Insufficient balance!</b>\nRequired: <b>{plan_price:,} UZS</b>\nNeed <b>{needed:,.0f} UZS</b> more."
            }
            return await callback.answer(msg.get(lang, msg["uz"]), show_alert=True)

        # Deduct balance & update dates
        client.balance -= plan_price
        client.plan_type = plan_name
        
        # Ensure UTC timezone is used
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # If dates are missing, tz-naive, or older than now
        end_date = client.plan_end_date
        
        if end_date:
            # If tz-naive, make it timezone-aware
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=datetime.timezone.utc)
                
        if not end_date or end_date < now:
            client.plan_start_date = now
            client.plan_end_date = now + datetime.timedelta(days=30)
        else:
            client.plan_end_date = end_date + datetime.timedelta(days=30)

        # Log spending
        await spending_crud.create_spending(
            session=session,
            role='client',
            user_id=user_id,
            amount=plan_price,
            spend=f"Tarif xarid ({plan_name})",
            bot_username=None,
            username=callback.from_user.username
        )
        
        await session.commit()
    
    success_msg = {
        "uz": "✅ Tarif muvaffaqiyatli uzaytirildi! Endi /start bosing.",
        "ru": "✅ Тариф успешно продлен! Нажмите /start.",
        "en": "✅ Plan successfully renewed! Press /start."
    }
    await callback.message.edit_text(success_msg.get(lang, success_msg["uz"]))
    await callback.answer(success_msg.get(lang, success_msg["uz"]), show_alert=True)
    
@router.callback_query(F.data.startswith("renew_plan_"))
async def handle_renew_plan(callback: CallbackQuery):
    plan_name = callback.data.replace("renew_plan_", "")
    await process_renewal(callback, plan_name)
