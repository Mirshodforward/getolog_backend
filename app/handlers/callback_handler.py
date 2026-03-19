from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from app.states import BotCreationStates, BotEditStates
from app.database import AsyncSessionLocal
from app.crud import get_client_by_user_id, update_client_balance, create_transaction, update_bot_process_id, get_bot_by_id, stop_client_bot, update_client_language, create_client_spending, get_client_bots, get_bot_users_count, create_deleted_bot, delete_client_bot, set_bot_stop_flag, update_bot_card_and_prices
from app.config import settings
from app.translations import get_text, _
import os
import signal
import asyncio
import logging
import subprocess
import sys
from pathlib import Path

router = Router()
logger = logging.getLogger(__name__)


# ==================== LANGUAGE SELECTION ====================

@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery) -> None:
    """Handle language selection"""
    from app.config import PLAN_CONFIG
    
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name
    lang = callback.data.split("_")[-1]  # uz, ru, or en

    # Update client language in database
    async with AsyncSessionLocal() as session:
        await update_client_language(session, user_id, lang)
        client = await get_client_by_user_id(session, user_id)

    # Check if client is new (no plan_type selected yet)
    if client and not client.plan_type:
        # New client - show plan selection
        lang_names = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}
        
        plans_info = {
            "free": {
                "uz": "🆓 Free (Bepul, 1 bot)",
                "ru": "🆓 Free (Бесплатно, 1 бот)",
                "en": "🆓 Free (Free, 1 bot)"
            },
            "standard": {
                "uz": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} so'm, 2 bot)",
                "ru": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} сум, 2 бота)",
                "en": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} UZS, 2 bots)"
            },
            "biznes": {
                "uz": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} so'm, 5 bot)",
                "ru": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} сум, 5 ботов)",
                "en": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} UZS, 5 bots)"
            }
        }
        
        keyboard_buttons = [
            [
                InlineKeyboardButton(text=plans_info["free"][lang], callback_data="plan_free"),
                InlineKeyboardButton(text=plans_info["standard"][lang], callback_data="plan_standard")
            ],
            [
                InlineKeyboardButton(text=plans_info["biznes"][lang], callback_data="plan_biznes")
            ]
        ]
        
        msg_parts = {
            "uz": f"✅ {lang_names.get(lang, lang)}\n\n💰 <b>Tarifni tanlang:</b>\n\n🆓 <b>Free</b> - Bepul, 1 ta bot\n📘 <b>Standard</b> - 97.000 so'm/oy, 2 ta bot\n🎯 <b>Biznes</b> - 497.000 so'm/oy, 5 ta bot",
            "ru": f"✅ {lang_names.get(lang, lang)}\n\n💰 <b>Выберите тариф:</b>\n\n🆓 <b>Free</b> - Бесплатно, 1 бот\n📘 <b>Standard</b> - 97.000 сум/мес, 2 бота\n🎯 <b>Biznes</b> - 497.000 сум/мес, 5 ботов",
            "en": f"✅ {lang_names.get(lang, lang)}\n\n💰 <b>Select a plan:</b>\n\n🆓 <b>Free</b> - Free, 1 bot\n📘 <b>Standard</b> - 97.000 UZS/month, 2 bots\n🎯 <b>Biznes</b> - 497.000 UZS/month, 5 bots"
        }
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            msg_parts.get(lang, msg_parts["uz"]),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Existing client - show main menu
        lang_names = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}

        # Create inline keyboard with translations
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            
            [InlineKeyboardButton(text=f"{_('btn_my_bots', lang)}", callback_data="my_bots")],
        ])

        balance = float(client.balance) if client and client.balance else 0
        balance_fmt = f"{balance:,.0f}".replace(',', ' ')
        plan_str = client.plan_type or "Free"

        def format_dt(dt):
            if not dt: return "N/A"
            if dt.tzinfo is None:
                import datetime
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            from app.config import TASHKENT_TZ
            return dt.astimezone(TASHKENT_TZ).strftime('%d.%m.%Y %H:%M')

        start_date_str = format_dt(client.plan_start_date) if client else "N/A"
        end_date_str = format_dt(client.plan_end_date) if client else "N/A"

        welcome_text = _('welcome', lang,
                         name=first_name,
                         balance=balance_fmt,
                         plan=plan_str.capitalize(),
                         start_date=start_date_str,
                         end_date=end_date_str)

        await callback.message.edit_text(
            f"✅ {lang_names.get(lang, lang)}\n\n"
            f"{welcome_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    await callback.answer()


# ==================== INITIAL PLAN SELECTION (after language) ====================

@router.callback_query(F.data == "plan_free")
async def select_initial_plan_free(callback: CallbackQuery) -> None:
    """Select free plan (initial selection or from bot creation)"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name
    
    # Update client plan in database
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if client:
            client.plan_type = "free"
            await session.commit()
            lang = client.language or "uz"
    
    # Show main menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
       
        [InlineKeyboardButton(text=f"{_('btn_my_bots', lang)}", callback_data="my_bots")],
    ])
    
    msg_plan = {
        "uz": "✅ <b>Free</b> tarifini tanladingiz!\n\n👋 Xush kelibsiz!",
        "ru": "✅ Вы выбрали тариф <b>Free</b>!\n\n👋 Добро пожаловать!",
        "en": "✅ You selected <b>Free</b> plan!\n\n👋 Welcome!"
    }
    
    await callback.message.edit_text(
        msg_plan.get(lang, msg_plan["uz"]),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "plan_standard")
async def select_initial_plan_standard(callback: CallbackQuery) -> None:
    """Select standard plan (initial selection or from bot creation)"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name
    
    # Update client plan in database
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if client:
            client.plan_type = "standard"
            await session.commit()
            lang = client.language or "uz"
    
    # Show main menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
     
        [InlineKeyboardButton(text=f"{_('btn_my_bots', lang)}", callback_data="my_bots")],
    ])
    
    msg_plan = {
        "uz": "✅ <b>Standard</b> tarifini tanladingiz!\n\n👋 Xush kelibsiz!",
        "ru": "✅ Вы выбрали тариф <b>Standard</b>!\n\n👋 Добро пожаловать!",
        "en": "✅ You selected <b>Standard</b> plan!\n\n👋 Welcome!"
    }
    
    await callback.message.edit_text(
        msg_plan.get(lang, msg_plan["uz"]),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "plan_biznes")
async def select_initial_plan_biznes(callback: CallbackQuery) -> None:
    """Select biznes plan (initial selection or from bot creation)"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name
    
    # Update client plan in database
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if client:
            client.plan_type = "biznes"
            await session.commit()
            lang = client.language or "uz"
    
    # Show main menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 {_('btn_create_bot', lang)}", callback_data="create_bot")],
        [InlineKeyboardButton(text=f"📋 {_('btn_my_bots', lang)}", callback_data="my_bots")],
    ])
    
    msg_plan = {
        "uz": "✅ <b>Biznes</b> tarifini tanladingiz!\n\n👋 Xush kelibsiz!",
        "ru": "✅ Вы выбрали тариф <b>Biznes</b>!\n\n👋 Добро пожаловать!",
        "en": "✅ You selected <b>Biznes</b> plan!\n\n👋 Welcome!"
    }
    
    await callback.message.edit_text(
        msg_plan.get(lang, msg_plan["uz"]),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "create_bot")
async def create_bot_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Create bot button callback - skip plan if already selected"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
    from app.config import PLAN_CONFIG

    user_id = callback.from_user.id

    # Check user balance and get language
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)

    current_balance = float(client.balance) if client and client.balance else 0
    lang = client.language if client else "uz"
    current_plan = client.plan_type if client else None

    # Save language in state for later use
    await state.update_data(lang=lang, plan=current_plan or "free")

    # If client already has a plan selected, go directly to contact request
    if current_plan:
        plan_names = {
            "free": {"uz": "Free", "ru": "Free", "en": "Free"},
            "standard": {"uz": "Standard", "ru": "Standard", "en": "Standard"},
            "biznes": {"uz": "Biznes", "ru": "Biznes", "en": "Biznes"}
        }
        
        msgs = {
            "uz": f"🤖 <b>Bot yaratish</b>\n\nSizning tarifingiz: <b>{plan_names[current_plan][lang]}</b>",
            "ru": f"🤖 <b>Создание бота</b>\n\nВаш тариф: <b>{plan_names[current_plan][lang]}</b>",
            "en": f"🤖 <b>Create Bot</b>\n\nYour plan: <b>{plan_names[current_plan][lang]}</b>"
        }

        from app.handlers.phone_helper import ask_for_phone_or_token
        await ask_for_phone_or_token(callback, state, lang, client, msgs)
        return

    plans_info = {
        "free": {
            "uz": "🆓 Free (Bepul, 1 bot)",
            "ru": "🆓 Free (Бесплатно, 1 бот)",
            "en": "🆓 Free (Free, 1 bot)"
        },
        "standard": {
            "uz": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} so'm, 2 bot)",
            "ru": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} сум, 2 бота)",
            "en": f"📘 Standard ({PLAN_CONFIG['standard']['price']:,} UZS, 2 bots)"
        },
        "biznes": {
            "uz": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} so'm, 5 bot)",
            "ru": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} сум, 5 ботов)",
            "en": f"🎯 Biznes ({PLAN_CONFIG['biznes']['price']:,} UZS, 5 bots)"
        }
    }

    # Add plan buttons
    keyboard_buttons = []
    keyboard_buttons.append([
        InlineKeyboardButton(text=plans_info["free"][lang], callback_data="plan_free"),
        InlineKeyboardButton(text=plans_info["standard"][lang], callback_data="plan_standard")
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(text=plans_info["biznes"][lang], callback_data="plan_biznes")
    ])
    
    # Add topup button
    topup_text = {"uz": "💳 Hisobni to'ldirish", "ru": "💳 Пополнить счёт", "en": "💳 Top up balance"}
    keyboard_buttons.append([InlineKeyboardButton(text=topup_text.get(lang, topup_text["uz"]), callback_data="topup_balance")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    msg_parts = {
        "uz": f"💰 <b>Tarifni tanlang</b>\n\nSizning balansingiz: <b>{current_balance:,.0f} so'm</b>\n\n🆓 <b>Free</b> - Bepul, 1 ta bot\n📘 <b>Standard</b> - 97.000 so'm/oy, 2 ta bot\n🎯 <b>Biznes</b> - 497.000 so'm/oy, 5 ta bot",
        "ru": f"💰 <b>Выберите тариф</b>\n\nВаш баланс: <b>{current_balance:,.0f} сум</b>\n\n🆓 <b>Free</b> - Бесплатно, 1 бот\n📘 <b>Standard</b> - 97.000 сум/мес, 2 бота\n🎯 <b>Biznes</b> - 497.000 сум/мес, 5 ботов",
        "en": f"💰 <b>Select a plan</b>\n\nYour balance: <b>{current_balance:,.0f} UZS</b>\n\n🆓 <b>Free</b> - Free, 1 bot\n📘 <b>Standard</b> - 97.000 UZS/month, 2 bots\n🎯 <b>Biznes</b> - 497.000 UZS/month, 5 bots"
    }

    await callback.message.edit_text(
        msg_parts.get(lang, msg_parts["uz"]),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(BotCreationStates.selecting_plan)
    await callback.answer()


@router.callback_query(BotCreationStates.selecting_plan, F.data == "plan_free")
async def select_free_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Select free plan"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(plan="free")

    # Button text translations
    from app.handlers.phone_helper import ask_for_phone_or_token
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, callback.from_user.id)
    await ask_for_phone_or_token(callback, state, lang, client)


@router.callback_query(BotCreationStates.selecting_plan, F.data == "plan_premium")
async def select_premium_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Select premium plan - check balance first"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

    user_id = callback.from_user.id
    PREMIUM_PRICE = settings.PREMIUM_PRICE

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Check user balance
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)

    current_balance = float(client.balance) if client and client.balance else 0

    # If balance is not enough
    if current_balance < PREMIUM_PRICE:
        needed = PREMIUM_PRICE - current_balance

        topup_text = {"uz": "💳 Hisobni to'ldirish", "ru": "💳 Пополнить счёт", "en": "💳 Top up balance"}
        back_text = {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"}

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=topup_text.get(lang, topup_text["uz"]), callback_data="topup_balance")],
            [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="create_bot")],
        ])

        msg = {
            "uz": f"⚠️ <b>Hisobingizda yetarli mablag' yo'q!</b>\n\nBalansingiz: <b>{current_balance:,.0f} so'm</b>\n\nIltimos hisobingizni <b>{needed:,.0f} so'mga</b> to'ldiring.\n",
            "ru": f"⚠️ <b>Недостаточно средств!</b>\n\nВаш баланс: <b>{current_balance:,.0f} сум</b>\n\nПополните счёт на <b>{needed:,.0f} сум</b>.\n",
            "en": f"⚠️ <b>Insufficient balance!</b>\n\nYour balance: <b>{current_balance:,.0f} UZS</b>\n\nPlease top up <b>{needed:,.0f} UZS</b>.\n"
        }

        await callback.message.edit_text(msg.get(lang, msg["uz"]), reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
        await callback.answer()
        return

    # If balance is enough - continue directly
    await state.update_data(plan="premium")

    from app.handlers.phone_helper import ask_for_phone_or_token
    await ask_for_phone_or_token(callback, state, lang, client)
    await callback.answer()


@router.callback_query(BotCreationStates.selecting_plan, F.data == "plan_standard")
async def select_standard_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Select standard plan - check balance first"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
    from app.config import PLAN_CONFIG

    user_id = callback.from_user.id
    plan_price = PLAN_CONFIG["standard"]["price"]

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Check user balance
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)

    current_balance = float(client.balance) if client and client.balance else 0

    # If balance is not enough
    if current_balance < plan_price:
        needed = plan_price - current_balance

        topup_text = {"uz": "💳 Hisobni to'ldirish", "ru": "💳 Пополнить счёт", "en": "💳 Top up balance"}
        back_text = {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"}

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=topup_text.get(lang, topup_text["uz"]), callback_data="topup_balance")],
            [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="create_bot")],
        ])

        msg = {
            "uz": f"⚠️ <b>Hisobingizda yetarli mablag' yo'q!</b>\n\nBalansingiz: <b>{current_balance:,.0f} so'm</b>\nKerakli: <b>{plan_price:,} so'm</b>\n\nIltimos hisobingizni <b>{needed:,.0f} so'mga</b> to'ldiring.\n",
            "ru": f"⚠️ <b>Недостаточно средств!</b>\n\nВаш баланс: <b>{current_balance:,.0f} сум</b>\nНужно: <b>{plan_price:,} сум</b>\n\nПополните счёт на <b>{needed:,.0f} сум</b>.\n",
            "en": f"⚠️ <b>Insufficient balance!</b>\n\nYour balance: <b>{current_balance:,.0f} UZS</b>\nRequired: <b>{plan_price:,} UZS</b>\n\nPlease top up <b>{needed:,.0f} UZS</b>.\n"
        }

        await callback.message.edit_text(msg.get(lang, msg["uz"]), reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
        await callback.answer()
        return

    # If balance is enough - continue directly
    await state.update_data(plan="standard")

    from app.handlers.phone_helper import ask_for_phone_or_token
    await ask_for_phone_or_token(callback, state, lang, client)
    await callback.answer()


@router.callback_query(BotCreationStates.selecting_plan, F.data == "plan_biznes")
async def select_biznes_plan(callback: CallbackQuery, state: FSMContext) -> None:
    """Select biznes plan - check balance first"""
    from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
    from app.config import PLAN_CONFIG

    user_id = callback.from_user.id
    plan_price = PLAN_CONFIG["biznes"]["price"]

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Check user balance
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)

    current_balance = float(client.balance) if client and client.balance else 0

    # If balance is not enough
    if current_balance < plan_price:
        needed = plan_price - current_balance

        topup_text = {"uz": "💳 Hisobni to'ldirish", "ru": "💳 Пополнить счёт", "en": "💳 Top up balance"}
        back_text = {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"}

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=topup_text.get(lang, topup_text["uz"]), callback_data="topup_balance")],
            [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="create_bot")],
        ])

        msg = {
            "uz": f"⚠️ <b>Hisobingizda yetarli mablag' yo'q!</b>\n\nBalansingiz: <b>{current_balance:,.0f} so'm</b>\nKerakli: <b>{plan_price:,} so'm</b>\n\nIltimos hisobingizni <b>{needed:,.0f} so'mga</b> to'ldiring.\n",
            "ru": f"⚠️ <b>Недостаточно средств!</b>\n\nВаш баланс: <b>{current_balance:,.0f} сум</b>\nНужно: <b>{plan_price:,} сум</b>\n\nПополните счёт на <b>{needed:,.0f} сум</b>.\n",
            "en": f"⚠️ <b>Insufficient balance!</b>\n\nYour balance: <b>{current_balance:,.0f} UZS</b>\nRequired: <b>{plan_price:,} UZS</b>\n\nPlease top up <b>{needed:,.0f} UZS</b>.\n"
        }

        await callback.message.edit_text(msg.get(lang, msg["uz"]), reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
        await callback.answer()
        return

    # If balance is enough - continue directly
    await state.update_data(plan="biznes")

    from app.handlers.phone_helper import ask_for_phone_or_token
    await ask_for_phone_or_token(callback, state, lang, client)
    await callback.answer()


@router.callback_query(BotCreationStates.admin_warning, F.data == "admin_understood")
async def admin_understood(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin understood warning"""
    from aiogram.types import ReplyKeyboardRemove

    data = await state.get_data()
    lang = data.get("lang", "uz")

    msg1 = {
        "uz": "💳 To'lov uchun karta raqamingizni kiriting:\n\nMijozlaringiz shu kartaga to'lov qilishadi\n\n(Humo/Uzcard 16 raqam, masalan: 9860350142898617):",
        "ru": "💳 Введите номер карты для приёма платежей:\n\nВаши клиенты будут платить на эту карту\n\n(Humo/Uzcard 16 цифр, например: 9860350142898617):",
        "en": "💳 Enter your card number for payments:\n\nYour clients will pay to this card\n\n(Humo/Uzcard 16 digits, e.g.: 9860350142898617):"
    }
    msg2 = {"uz": "Karta raqamini kiriting:", "ru": "Введите номер карты:", "en": "Enter card number:"}

    await callback.message.edit_text(msg1.get(lang, msg1["uz"]))
    await callback.message.answer(msg2.get(lang, msg2["uz"]), reply_markup=ReplyKeyboardRemove())
    await state.set_state(BotCreationStates.entering_card_number)
    await callback.answer()


@router.callback_query(F.data == "my_bots")
async def my_bots_callback(callback: CallbackQuery) -> None:
    """My bots button callback - show bots as inline buttons based on plan limit"""
    import datetime
    
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        # Get client for language and details
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        # Get all client bots for this user
        bots = await get_client_bots(session, user_id)

    # Determine limits
    current_plan = "free"
    # Check plan validity
    if client and client.plan_type in ["standard", "standart", "biznes"]:
        now_tz = datetime.datetime.now(datetime.timezone.utc)
        if client.plan_end_date:
            end_date = client.plan_end_date
            if end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=datetime.timezone.utc)
                
            if end_date > now_tz:
                current_plan = client.plan_type
        else:
            current_plan = client.plan_type

    if current_plan == "biznes":
        bot_limit = settings.BIZNES_PLAN_BOT_LIMIT
    elif current_plan == "standard":
        bot_limit = settings.STANDARD_PLAN_BOT_LIMIT
    else:
        bot_limit = settings.FREE_PLAN_BOT_LIMIT

    balance = float(client.balance) if client and client.balance else 0

    def format_dt(dt):
        if not dt: return "N/A"
        if dt.tzinfo is None:
            import datetime
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        from app.config import TASHKENT_TZ
        return dt.astimezone(TASHKENT_TZ).strftime('%d.%m.%Y %H:%M')

    start_str = format_dt(client.plan_start_date) if client else "N/A"
    end_str = format_dt(client.plan_end_date) if client else "N/A"
    plan_name = current_plan.capitalize()

    msg_text = {
        "uz": (
            "📋 <b>Mening botlarim:</b>\n\n"
            f"💰 Balansingiz: <b>{balance:,.0f} so'm</b>\n"
            f"💎 Tarifingiz: <b>{plan_name}</b>\n"
            f"📅 Muddat: <b>{start_str}</b> dan <b>{end_str}</b> gacha\n\n"
            "👇 Botni boshqarish uchun ustiga bosing yoki yangi bot qo'shing:"
        ),
        "ru": (
            "📋 <b>Мои боты:</b>\n\n"
            f"💰 Ваш баланс: <b>{balance:,.0f} сум</b>\n"
            f"💎 Ваш тариф: <b>{plan_name}</b>\n"
            f"📅 Срок: от <b>{start_str}</b> до <b>{end_str}</b>\n\n"
            "👇 Нажмите на бота для управления или добавьте нового:"
        ),
        "en": (
            "📋 <b>My bots:</b>\n\n"
            f"💰 Your balance: <b>{balance:,.0f} UZS</b>\n"
            f"💎 Your plan: <b>{plan_name}</b>\n"
            f"📅 Period: from <b>{start_str}</b> to <b>{end_str}</b>\n\n"
            "👇 Click on a bot to manage or add a new one:"
        )
    }

    keyboard_buttons = []
    
    # Render slots
    total_slots = max(bot_limit, len(bots))
    for i in range(total_slots):
        if i < len(bots):
            bot = bots[i]
            status_icon = "✅" if bot.status == "active" else "⏸️" if bot.status == "stopped" else "🆓"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{status_icon} @{bot.bot_username}",
                    callback_data=f"bot_manage_{bot.id}"
                )
            ])
        else:
            btn_add_text = {
                "uz": "➕ Yangi bot",
                "ru": "➕ Новый бот",
                "en": "➕ New bot"
            }
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=btn_add_text.get(lang, btn_add_text["uz"]),
                    callback_data="create_bot"
                )
            ])

    # Add back button
    back_text = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    keyboard_buttons.append([
        InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="back_to_main")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(
        msg_text.get(lang, msg_text["uz"]),
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("bot_manage_"))
async def bot_manage_callback(callback: CallbackQuery) -> None:
    """Show bot management options (Edit/Delete)"""
    bot_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"
        
        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {
                "uz": "❌ Bot topilmadi!",
                "ru": "❌ Бот не найден!",
                "en": "❌ Bot not found!"
            }
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

        # Get user count for this bot
        users_count = await get_bot_users_count(session, user_id)

    status_text = {
        "active": {"uz": "✅ Faol", "ru": "✅ Активен", "en": "✅ Active"},
        "stopped": {"uz": "⏸️ To'xtatilgan", "ru": "⏸️ Остановлен", "en": "⏸️ Stopped"},
        "free": {"uz": "🆓 Bepul", "ru": "🆓 Бесплатный", "en": "🆓 Free"}
    }

    # Build info text
    info_text = f"🤖 <b>Bot Ma'lumotlari</b>\n\n"
    info_text += f"📊 Status: {status_text.get(bot.status, status_text['free']).get(lang, status_text['free']['uz'])}\n"
    info_text += f"👥 {'Foydalanuvchilar' if lang == 'uz' else 'Пользователи' if lang == 'ru' else 'Users'}: {users_count}\n"
    if bot.bot_username:
        info_text += f"🔗 <b>@{bot.bot_username}</b>\n\n"
        
    currency = "so'm" if lang == 'uz' else 'сум' if lang == 'ru' else 'UZS'
    
    if bot.oy_narx is not None:
        oy_label = 'Oylik' if lang == 'uz' else 'Месяц' if lang == 'ru' else 'Monthly'
        info_text += f"💵 {oy_label}: <b>{bot.oy_narx:,.0f}</b> {currency}\n"
        
    if bot.yil_narx is not None:
        yil_label = 'Yillik' if lang == 'uz' else 'Год' if lang == 'ru' else 'Yearly'
        info_text += f"💰 {yil_label}: <b>{bot.yil_narx:,.0f}</b> {currency}\n"
        
    if bot.cheksiz_narx is not None:
        chek_label = 'Cheksiz' if lang == 'uz' else 'Навсегда' if lang == 'ru' else 'Lifetime'
        info_text += f"💎 {chek_label}: <b>{bot.cheksiz_narx:,.0f}</b> {currency}\n"
        
    if bot.card_number:
        card_label = 'Karta' if lang == 'uz' else 'Карта' if lang == 'ru' else 'Card'
        info_text += f"\n💳 {card_label}: <code>{bot.card_number}</code>\n"
        
    if bot.channel_id:
        chan_label = 'Kanal ID' if lang == 'uz' else 'ID Канала' if lang == 'ru' else 'Channel ID'
        info_text += f"📢 {chan_label}: <code>{bot.channel_id}</code>\n"
        
    if getattr(bot, "manager_invite_link", None):
        link_label = 'Kanal havolasi' if lang == 'uz' else 'Ссылка на канал' if lang == 'ru' else 'Channel link'
        info_text += f"🌐 {link_label}: {bot.manager_invite_link}\n"

    edit_text = {"uz": "✏️ Tahrirlash", "ru": "✏️ Редактировать", "en": "✏️ Edit"}
    delete_text = {"uz": "🗑 O'chirish", "ru": "🗑 Удалить", "en": "🗑 Delete"}
    back_text = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=edit_text.get(lang, edit_text["uz"]), callback_data=f"bot_edit_{bot_id}"),
            InlineKeyboardButton(text=delete_text.get(lang, delete_text["uz"]), callback_data=f"bot_delete_{bot_id}")
        ],
        [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="my_bots")]
    ])

    await callback.message.edit_text(info_text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_delete_") & ~F.data.startswith("bot_delete_confirm_") & ~F.data.startswith("bot_delete_cancel_"))
async def bot_delete_callback(callback: CallbackQuery) -> None:
    """Show delete confirmation"""
    bot_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"
        
        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {
                "uz": "❌ Bot topilmadi!",
                "ru": "❌ Бот не найден!",
                "en": "❌ Bot not found!"
            }
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

    confirm_msg = {
        "uz": f"⚠️ <b>Diqqat!</b>\n\n<b>{bot.bot_username}</b> botini o'chirmoqchimisiz?\n\nBu amalni ortga qaytarib bo'lmaydi!",
        "ru": f"⚠️ <b>Внимание!</b>\n\nВы хотите удалить бота <b>{bot.bot_username}</b>?\n\nЭто действие нельзя отменить!",
        "en": f"⚠️ <b>Warning!</b>\n\nDo you want to delete <b>{bot.bot_username}</b>?\n\nThis action cannot be undone!"
    }
    
    confirm_text = {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "en": "✅ Confirm"}
    cancel_text = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=confirm_text.get(lang, confirm_text["uz"]), callback_data=f"bot_delete_confirm_{bot_id}"),
            InlineKeyboardButton(text=cancel_text.get(lang, cancel_text["uz"]), callback_data=f"bot_delete_cancel_{bot_id}")
        ]
    ])

    await callback.message.edit_text(confirm_msg.get(lang, confirm_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_delete_confirm_"))
async def bot_delete_confirm_callback(callback: CallbackQuery) -> None:
    """Confirm bot deletion - stop bot, archive to deleted_bots, remove from client_bots"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"
        
        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {
                "uz": "❌ Bot topilmadi!",
                "ru": "❌ Бот не найден!",
                "en": "❌ Bot not found!"
            }
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

        try:
            # 1. Stop the bot if it's running
            if bot.status == "active":
                from app.bot_manager import stop_bot_task
                stop_bot_task(bot.bot_token)
                logger.info(f"Bot task for {bot.bot_token[:10]} stopped for deletion")

            # 2. Get users count for this bot
            users_count = await get_bot_users_count(session, user_id)

            # 3. Archive bot to deleted_bots
            await create_deleted_bot(session, bot, users_count, reason="User requested deletion")

            # 4. Delete from client_bots
            await delete_client_bot(session, bot_id)

            success_msg = {
                "uz": f"✅ <b>{bot.bot_username}</b> boti muvaffaqiyatli o'chirildi!",
                "ru": f"✅ Бот <b>{bot.bot_username}</b> успешно удалён!",
                "en": f"✅ Bot <b>{bot.bot_username}</b> successfully deleted!"
            }

            back_text = {"uz": "⬅️ Botlarimga qaytish", "ru": "⬅️ К моим ботам", "en": "⬅️ Back to my bots"}
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=back_text.get(lang, back_text["uz"]), callback_data="my_bots")]
            ])

            await callback.message.edit_text(success_msg.get(lang, success_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
            logger.info(f"Bot {bot.bot_username} (ID: {bot_id}) deleted by user {user_id}")

        except Exception as e:
            logger.error(f"Error deleting bot {bot_id}: {e}")
            error_msg = {
                "uz": "❌ Xatolik yuz berdi! Qayta urinib ko'ring.",
                "ru": "❌ Произошла ошибка! Попробуйте снова.",
                "en": "❌ An error occurred! Please try again."
            }
            await callback.message.edit_text(error_msg.get(lang, error_msg["uz"]))

    await callback.answer()


@router.callback_query(F.data.startswith("bot_delete_cancel_"))
async def bot_delete_cancel_callback(callback: CallbackQuery) -> None:
    """Cancel bot deletion - go back to bot management"""
    bot_id = int(callback.data.split("_")[3])
    
    # Trigger bot_manage callback
    callback.data = f"bot_manage_{bot_id}"
    await bot_manage_callback(callback)


@router.callback_query(F.data.startswith("bot_edit_") & ~F.data.startswith("bot_edit_card_") & ~F.data.startswith("bot_edit_prices_") & ~F.data.startswith("bot_edit_confirm_") & ~F.data.startswith("bot_edit_cancel_"))
async def bot_edit_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Bot edit callback - show edit options (card or prices)"""
    bot_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {
                "uz": "❌ Bot topilmadi!",
                "ru": "❌ Бот не найден!",
                "en": "❌ Bot not found!"
            }
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

    # Save bot_id and lang in state
    await state.update_data(edit_bot_id=bot_id, lang=lang)

    edit_title = {
        "uz": f"✏️ <b>{bot.bot_username}</b> tahrirlash\n\nNimani o'zgartirmoqchisiz?",
        "ru": f"✏️ Редактирование <b>{bot.bot_username}</b>\n\nЧто хотите изменить?",
        "en": f"✏️ Edit <b>{bot.bot_username}</b>\n\nWhat would you like to change?"
    }

    card_btn = {"uz": "💳 Karta raqami", "ru": "💳 Номер карты", "en": "💳 Card number"}
    prices_btn = {"uz": "💰 Narxlar", "ru": "💰 Цены", "en": "💰 Prices"}
    
    ads_status = "🟢 Yoqilgan" if client.switch_ads else "🔴 O'chirilgan"
    ads_status_ru = "🟢 Включена" if client.switch_ads else "🔴 Отключена"
    ads_status_en = "🟢 Enabled" if client.switch_ads else "🔴 Disabled"
    
    ads_btn = {
        "uz": f"📢 Reklama: {ads_status}", 
        "ru": f"📢 Реклама: {ads_status_ru}", 
        "en": f"📢 Ads: {ads_status_en}"
    }
    
    back_btn = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=card_btn.get(lang, card_btn["uz"]), callback_data=f"bot_edit_card_{bot_id}"),
            InlineKeyboardButton(text=prices_btn.get(lang, prices_btn["uz"]), callback_data=f"bot_edit_prices_{bot_id}")
        ],
        [
            InlineKeyboardButton(text=ads_btn.get(lang, ads_btn["uz"]), callback_data=f"bot_toggle_ads_{bot_id}")
        ],
        [InlineKeyboardButton(text=back_btn.get(lang, back_btn["uz"]), callback_data=f"bot_manage_{bot_id}")]
    ])

    await callback.message.edit_text(edit_title.get(lang, edit_title["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.selecting_field)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_toggle_ads_"))
async def bot_toggle_ads_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Toggle Ads logic"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    import datetime

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if not client:
            return
            
        lang = client.language if client else "uz"
        
        # Check plan
        has_plan = False
        if getattr(client, "plan_type", None) in ["standard", "standart", "biznes"]:
            if client.plan_end_date:
                now_tz = datetime.datetime.now(datetime.timezone.utc)
                end_date = client.plan_end_date
                if end_date.tzinfo is None:
                    end_date = end_date.replace(tzinfo=datetime.timezone.utc)
                if end_date > now_tz:
                    has_plan = True
            else:
                has_plan = True
                
        if not has_plan:
            errors = {
                "uz": "❌ Reklamani o'chirish uchun tarif sotib olishingiz kerak!",
                "ru": "❌ Вам нужно купить тариф, чтобы отключить рекламу!",
                "en": "❌ You need to buy a plan to disable ads!"
            }
            await callback.answer(errors.get(lang, errors["uz"]), show_alert=True)
            return
            
        # Toggle boolean
        client.switch_ads = not client.switch_ads
        await session.commit()
        
        # Redraw keyboard manually
        ads_status = "🟢 Yoqilgan" if client.switch_ads else "🔴 O'chirilgan"
        ads_status_ru = "🟢 Включена" if client.switch_ads else "🔴 Отключена"
        ads_status_en = "🟢 Enabled" if client.switch_ads else "🔴 Disabled"
        
        ads_btn = {
            "uz": f"📢 Reklama: {ads_status}",
            "ru": f"📢 Реклама: {ads_status_ru}",
            "en": f"📢 Ads: {ads_status_en}"
        }
        
        card_btn = {"uz": "💳 Karta raqami", "ru": "💳 Номер карты", "en": "💳 Card number"}
        prices_btn = {"uz": "💰 Narxlar", "ru": "💰 Цены", "en": "💰 Prices"}
        back_btn = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=card_btn.get(lang, card_btn["uz"]), callback_data=f"bot_edit_card_{bot_id}"),
                InlineKeyboardButton(text=prices_btn.get(lang, prices_btn["uz"]), callback_data=f"bot_edit_prices_{bot_id}")
            ],
            [
                InlineKeyboardButton(text=ads_btn.get(lang, ads_btn["uz"]), callback_data=f"bot_toggle_ads_{bot_id}")
            ],
            [InlineKeyboardButton(text=back_btn.get(lang, back_btn["uz"]), callback_data=f"bot_manage_{bot_id}")]
        ])
        
        await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(F.data.startswith("bot_edit_card_"))
async def bot_edit_card_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Edit card number - stop bot and ask for new card"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {"uz": "❌ Bot topilmadi!", "ru": "❌ Бот не найден!", "en": "❌ Bot not found!"}
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

        # Stop bot by setting should_stop flag
        await set_bot_stop_flag(session, bot_id, should_stop=True)

        current_card = bot.card_number or "----"

    # Save data in state
    await state.update_data(edit_bot_id=bot_id, lang=lang, edit_type="card")

    stopping_msg = {
        "uz": f"⏳ <b>{bot.bot_username}</b> to'xtatilmoqda...\n\nO'zgarishlar kiritish uchun bot vaqtincha to'xtatiladi.",
        "ru": f"⏳ <b>{bot.bot_username}</b> останавливается...\n\nБот временно остановлен для внесения изменений.",
        "en": f"⏳ <b>{bot.bot_username}</b> is stopping...\n\nBot is temporarily stopped for editing."
    }
    await callback.message.edit_text(stopping_msg.get(lang, stopping_msg["uz"]), parse_mode="HTML")

    # Wait for bot to stop (bot checks every 5 seconds, so wait 7 seconds)
    await asyncio.sleep(7)

    enter_card_msg = {
        "uz": f"💳 Yangi karta raqamini kiriting (16 raqam):\n\nJoriy karta: <code>{current_card}</code>",
        "ru": f"💳 Введите новый номер карты (16 цифр):\n\nТекущая карта: <code>{current_card}</code>",
        "en": f"💳 Enter new card number (16 digits):\n\nCurrent card: <code>{current_card}</code>"
    }

    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await callback.message.edit_text(enter_card_msg.get(lang, enter_card_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.editing_card)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_edit_prices_"))
async def bot_edit_prices_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Edit prices - stop bot and ask for new prices"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        bot = await get_bot_by_id(session, bot_id)
        if not bot or bot.user_id != user_id:
            error_msg = {"uz": "❌ Bot topilmadi!", "ru": "❌ Бот не найден!", "en": "❌ Bot not found!"}
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

        # Stop bot by setting should_stop flag
        await set_bot_stop_flag(session, bot_id, should_stop=True)

        current_oy = float(bot.oy_narx) if bot.oy_narx else 0
        current_yil = float(bot.yil_narx) if bot.yil_narx else 0
        current_cheksiz = float(bot.cheksiz_narx) if bot.cheksiz_narx else 0

    # Save data in state
    await state.update_data(
        edit_bot_id=bot_id,
        lang=lang,
        edit_type="prices",
        current_oy=current_oy,
        current_yil=current_yil,
        current_cheksiz=current_cheksiz
    )

    stopping_msg = {
        "uz": f"⏳ <b>{bot.bot_username}</b> to'xtatilmoqda...\n\nO'zgarishlar kiritish uchun bot vaqtincha to'xtatiladi.",
        "ru": f"⏳ <b>{bot.bot_username}</b> останавливается...\n\nБот временно остановлен для внесения изменений.",
        "en": f"⏳ <b>{bot.bot_username}</b> is stopping...\n\nBot is temporarily stopped for editing."
    }
    await callback.message.edit_text(stopping_msg.get(lang, stopping_msg["uz"]), parse_mode="HTML")

    # Wait for bot to stop (bot checks every 5 seconds, so wait 7 seconds)
    await asyncio.sleep(7)

    enter_oy_msg = {
        "uz": f"💰 Yangi <b>oylik</b> narxni kiriting (so'm):\n\nJoriy narx: <code>{current_oy:,.0f}</code> so'm",
        "ru": f"💰 Введите новую <b>месячную</b> цену (сум):\n\nТекущая цена: <code>{current_oy:,.0f}</code> сум",
        "en": f"💰 Enter new <b>monthly</b> price (UZS):\n\nCurrent price: <code>{current_oy:,.0f}</code> UZS"
    }

    skip_btn = {"uz": "⏭ O'tkazib yuborish", "ru": "⏭ Пропустить", "en": "⏭ Skip"}
    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_btn.get(lang, skip_btn["uz"]), callback_data=f"bot_edit_skip_oy_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await callback.message.edit_text(enter_oy_msg.get(lang, enter_oy_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.editing_oy_narx)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_edit_skip_oy_"))
async def bot_edit_skip_oy_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Skip monthly price edit, move to yearly"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")
    current_yil = data.get("current_yil", 0)

    # Keep current oy_narx
    await state.update_data(new_oy_narx=None)

    enter_yil_msg = {
        "uz": f"💰 Yangi <b>yillik</b> narxni kiriting (so'm):\n\nJoriy narx: <code>{current_yil:,.0f}</code> so'm",
        "ru": f"💰 Введите новую <b>годовую</b> цену (сум):\n\nТекущая цена: <code>{current_yil:,.0f}</code> сум",
        "en": f"💰 Enter new <b>yearly</b> price (UZS):\n\nCurrent price: <code>{current_yil:,.0f}</code> UZS"
    }

    skip_btn = {"uz": "⏭ O'tkazib yuborish", "ru": "⏭ Пропустить", "en": "⏭ Skip"}
    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_btn.get(lang, skip_btn["uz"]), callback_data=f"bot_edit_skip_yil_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await callback.message.edit_text(enter_yil_msg.get(lang, enter_yil_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.editing_yil_narx)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_edit_skip_yil_"))
async def bot_edit_skip_yil_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Skip yearly price edit, move to unlimited"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")
    current_cheksiz = data.get("current_cheksiz", 0)

    # Keep current yil_narx
    await state.update_data(new_yil_narx=None)

    enter_cheksiz_msg = {
        "uz": f"💰 Yangi <b>cheksiz</b> narxni kiriting (so'm):\n\nJoriy narx: <code>{current_cheksiz:,.0f}</code> so'm",
        "ru": f"💰 Введите новую <b>безлимитную</b> цену (сум):\n\nТекущая цена: <code>{current_cheksiz:,.0f}</code> сум",
        "en": f"💰 Enter new <b>unlimited</b> price (UZS):\n\nCurrent price: <code>{current_cheksiz:,.0f}</code> UZS"
    }

    skip_btn = {"uz": "⏭ O'tkazib yuborish", "ru": "⏭ Пропустить", "en": "⏭ Skip"}
    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_btn.get(lang, skip_btn["uz"]), callback_data=f"bot_edit_skip_cheksiz_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await callback.message.edit_text(enter_cheksiz_msg.get(lang, enter_cheksiz_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.editing_cheksiz_narx)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_edit_skip_cheksiz_"))
async def bot_edit_skip_cheksiz_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Skip unlimited price edit, show confirmation"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")

    # Keep current cheksiz_narx
    await state.update_data(new_cheksiz_narx=None)

    # Show confirmation
    await show_edit_confirmation(callback, state)


@router.callback_query(F.data.startswith("bot_edit_cancel_"))
async def bot_edit_cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel editing - restart bot without changes"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        bot = await get_bot_by_id(session, bot_id)
        if bot:
            # Reset stop flag to restart bot
            await set_bot_stop_flag(session, bot_id, should_stop=False)

    await state.clear()

    cancel_msg = {
        "uz": "❌ Tahrirlash bekor qilindi.\n\nBot qayta ishga tushirildi.",
        "ru": "❌ Редактирование отменено.\n\nБот перезапущен.",
        "en": "❌ Edit cancelled.\n\nBot restarted."
    }

    back_btn = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_btn.get(lang, back_btn["uz"]), callback_data=f"bot_manage_{bot_id}")]
    ])

    await callback.message.edit_text(cancel_msg.get(lang, cancel_msg["uz"]), reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_edit_confirm_"))
async def bot_edit_confirm_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirm changes and restart bot"""
    bot_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "uz")

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        bot = await get_bot_by_id(session, bot_id)

        if not bot or bot.user_id != user_id:
            error_msg = {"uz": "❌ Bot topilmadi!", "ru": "❌ Бот не найден!", "en": "❌ Bot not found!"}
            await callback.answer(error_msg.get(lang, error_msg["uz"]), show_alert=True)
            return

        # Apply changes
        edit_type = data.get("edit_type")

        if edit_type == "card":
            new_card = data.get("new_card")
            if new_card:
                await update_bot_card_and_prices(session, bot_id, card_number=new_card)

        elif edit_type == "prices":
            new_oy = data.get("new_oy_narx")
            new_yil = data.get("new_yil_narx")
            new_cheksiz = data.get("new_cheksiz_narx")
            await update_bot_card_and_prices(
                session, bot_id,
                oy_narx=new_oy,
                yil_narx=new_yil,
                cheksiz_narx=new_cheksiz
            )

        # Reset stop flag to restart bot
        await set_bot_stop_flag(session, bot_id, should_stop=False)

    await state.clear()

    restarting_msg = {
        "uz": "⏳ Bot qayta ishga tushirilmoqda...",
        "ru": "⏳ Бот перезапускается...",
        "en": "⏳ Bot is restarting..."
    }
    await callback.message.edit_text(restarting_msg.get(lang, restarting_msg["uz"]))

    # Wait for bot to restart
    await asyncio.sleep(2)

    success_msg = {
        "uz": "✅ O'zgarishlar saqlandi va bot muvaffaqiyatli qayta ishga tushirildi!",
        "ru": "✅ Изменения сохранены и бот успешно перезапущен!",
        "en": "✅ Changes saved and bot restarted successfully!"
    }

    back_btn = {"uz": "⬅️ Botga qaytish", "ru": "⬅️ К боту", "en": "⬅️ Back to bot"}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_btn.get(lang, back_btn["uz"]), callback_data=f"bot_manage_{bot_id}")]
    ])

    await callback.message.edit_text(success_msg.get(lang, success_msg["uz"]), reply_markup=keyboard)
    await callback.answer()


async def show_edit_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """Show confirmation screen with all changes"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")
    edit_type = data.get("edit_type")

    if edit_type == "card":
        new_card = data.get("new_card", "----")
        confirm_msg = {
            "uz": f"✅ <b>O'zgarishlar</b>\n\n💳 Yangi karta: <code>{new_card}</code>\n\n🔄 Botni qayta ishga tushirish uchun <b>Tasdiqlash</b> tugmasini bosing.",
            "ru": f"✅ <b>Изменения</b>\n\n💳 Новая карта: <code>{new_card}</code>\n\n🔄 Нажмите <b>Подтвердить</b> для перезапуска бота.",
            "en": f"✅ <b>Changes</b>\n\n💳 New card: <code>{new_card}</code>\n\n🔄 Press <b>Confirm</b> to restart the bot."
        }
    else:
        # Prices
        new_oy = data.get("new_oy_narx")
        new_yil = data.get("new_yil_narx")
        new_cheksiz = data.get("new_cheksiz_narx")
        current_oy = data.get("current_oy", 0)
        current_yil = data.get("current_yil", 0)
        current_cheksiz = data.get("current_cheksiz", 0)

        oy_display = f"{new_oy:,.0f}" if new_oy else f"{current_oy:,.0f} (o'zgarmadi)" if lang == "uz" else f"{current_oy:,.0f} (без изменений)" if lang == "ru" else f"{current_oy:,.0f} (unchanged)"
        yil_display = f"{new_yil:,.0f}" if new_yil else f"{current_yil:,.0f} (o'zgarmadi)" if lang == "uz" else f"{current_yil:,.0f} (без изменений)" if lang == "ru" else f"{current_yil:,.0f} (unchanged)"
        cheksiz_display = f"{new_cheksiz:,.0f}" if new_cheksiz else f"{current_cheksiz:,.0f} (o'zgarmadi)" if lang == "uz" else f"{current_cheksiz:,.0f} (без изменений)" if lang == "ru" else f"{current_cheksiz:,.0f} (unchanged)"

        currency = "so'm" if lang == "uz" else "сум" if lang == "ru" else "UZS"

        confirm_msg = {
            "uz": f"✅ <b>O'zgarishlar</b>\n\n💰 Oylik: {oy_display} {currency}\n💰 Yillik: {yil_display} {currency}\n💰 Cheksiz: {cheksiz_display} {currency}\n\n🔄 Botni qayta ishga tushirish uchun <b>Tasdiqlash</b> tugmasini bosing.",
            "ru": f"✅ <b>Изменения</b>\n\n💰 Месяц: {oy_display} {currency}\n💰 Год: {yil_display} {currency}\n💰 Безлимит: {cheksiz_display} {currency}\n\n🔄 Нажмите <b>Подтвердить</b> для перезапуска бота.",
            "en": f"✅ <b>Changes</b>\n\n💰 Monthly: {oy_display} {currency}\n💰 Yearly: {yil_display} {currency}\n💰 Unlimited: {cheksiz_display} {currency}\n\n🔄 Press <b>Confirm</b> to restart the bot."
        }

    confirm_btn = {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "en": "✅ Confirm"}
    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=confirm_btn.get(lang, confirm_btn["uz"]), callback_data=f"bot_edit_confirm_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await callback.message.edit_text(confirm_msg.get(lang, confirm_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.confirming_changes)
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback: CallbackQuery) -> None:
    """Go back to main menu"""
    user_id = callback.from_user.id
    first_name = callback.from_user.first_name

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

        if client:
            def format_welcome_dt(dt):
                if not dt: return "---"
                if dt.tzinfo is None:
                    import datetime
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                from app.config import TASHKENT_TZ
                return dt.astimezone(TASHKENT_TZ).strftime('%Y-%m-%d %H:%M')

            start_date_str = format_welcome_dt(getattr(client, 'plan_start_date', None))
            end_date_str = format_welcome_dt(getattr(client, 'plan_end_date', None))
            balance_fmt = f"{client.balance or 0:,.0f}".replace(",", " ")
            plan_str = getattr(client, 'plan_type', 'Free') or "Free"
        else:
            start_date_str = "---"
            end_date_str = "---"
            balance_fmt = "0"
            plan_str = "Free"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{_('btn_my_bots', lang)}", callback_data="my_bots")],
        [InlineKeyboardButton(text=f"{_('btn_buy_plan', lang)}", callback_data="buy_plan")],
    ])

    welcome_text = _('welcome', lang, 
                     name=first_name, 
                     balance=balance_fmt, 
                     plan=plan_str.capitalize(),
                     start_date=start_date_str,
                     end_date=end_date_str)

    await callback.message.edit_text(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(BotCreationStates.confirming_terms, F.data == "confirm_terms")
async def confirm_terms(callback: CallbackQuery, state: FSMContext) -> None:
    """Confirm and save bot, then launch it"""
    import sys
    import logging
    from pathlib import Path
    from datetime import datetime

    logger = logging.getLogger(__name__)
    user_id = callback.from_user.id
    data = await state.get_data()
    bot_instance = callback.bot  # Get bot instance for sending messages
    
    import asyncio
    import time

    async with AsyncSessionLocal() as session:
        from app.crud import create_client_bot
        # Update client with terms
        client = await get_client_by_user_id(session, user_id)
        if client:
            # If premium plan and NOT already premium - check balance and deduct
            if data['plan'] == 'premium' and not data.get('already_premium'):
                premium_price = settings.PREMIUM_PRICE
                current_balance = float(client.balance) if client.balance else 0

                # Double-check balance
                if current_balance < premium_price:
                    lang = data.get("lang", "uz")
                    error_msgs = {
                        "uz": f"❌ <b>Xatolik!</b>\n\nHisobingizda yetarli mablag' yo'q.\nKerakli: {premium_price:,} so'm\nMavjud: {current_balance:,.0f} so'm\n\n/balance - Hisobni to'ldirish",
                        "ru": f"❌ <b>Ошибка!</b>\n\nНедостаточно средств.\nНужно: {premium_price:,} сум\nДоступно: {current_balance:,.0f} сум\n\n/balance - Пополнить счёт",
                        "en": f"❌ <b>Error!</b>\n\nInsufficient balance.\nRequired: {premium_price:,} UZS\nAvailable: {current_balance:,.0f} UZS\n\n/balance - Top up balance"
                    }
                    await callback.message.edit_text(error_msgs.get(lang, error_msgs["uz"]), parse_mode="HTML")
                    await state.clear()
                    await callback.answer()
                    return

                # Deduct from balance
                await update_client_balance(session, user_id, -premium_price)

                # Create payment transaction
                username = callback.from_user.username or "Noma'lum"
                await create_transaction(
                    session=session,
                    user_id=user_id,
                    username=username,
                    amount=-premium_price,
                    role="payment",
                    status="approved"
                )

                # Create spending record for client
                await create_client_spending(
                    session=session,
                    user_id=user_id,
                    amount=premium_price,
                    spend="premium",
                    username=username
                )

            client.terms = True
            client.plan_type = data['plan']
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            client.plan_start_date = now
            if data['plan'] != 'free':
                client.plan_end_date = now + datetime.timedelta(days=30)

        # Create bot
        created_bot = await create_client_bot(
            session,
            user_id=user_id,
            bot_username=data['bot_username'],
            bot_token=data['bot_token'],
            channel_id=int(data['channel_link']),  # Changed to channel_id
            card_number=data['card_number'],
            oy_narx=data['oy_narx'],
            yil_narx=data['yil_narx'],
            cheksiz_narx=data['cheksiz_narx'],
            status="active"
        )

        bot_id = created_bot.id

    # Get language for messages
    lang = data.get("lang", "uz")

    # Show starting message
    starting_msgs = {
        "uz": "⏳ <b>Bot ishga tushyapti...</b>\n\nIltimos kuting, tekshirilmoqda...",
        "ru": "⏳ <b>Бот запускается...</b>\n\nПожалуйста, подождите...",
        "en": "⏳ <b>Bot is starting...</b>\n\nPlease wait..."
    }
    await callback.message.edit_text(starting_msgs.get(lang, starting_msgs["uz"]), parse_mode="HTML")
    project_root = Path(__file__).resolve().parent.parent.parent
    clients_bot_path = project_root / "client_bot_main.py"
    
    logger.info(f"🚀 Bot launch started: {data['bot_username']}")
    logger.info(f"📝 Token: {data['bot_token'][:20]}...")
    logger.info(f"🤖 Name: {data['bot_username']}")
    logger.info(f"👤 Owner ID: {user_id}")

    from app.bot_manager import run_bot_in_background
    await run_bot_in_background(
        bot_token=data['bot_token'],
        bot_username=data['bot_username'],
        owner_id=user_id
    )

    # Wait a bit for bot to start and retrieve metadata
    await asyncio.sleep(2)

    # Now check bot status and admin privilege
    bot_username = None
    is_admin = False
    admin_check_failed = False
    channel_id = int(data['channel_link'])

    try:
        # Create temporary bot instance to check status
        temp_bot = Bot(token=data['bot_token'])
        
        # Get bot info
        bot_id_in_db = None
        telegram_bot_id = None
        try:
            bot_info = await temp_bot.get_me()
            bot_username = bot_info.username
            telegram_bot_id = bot_info.id
            logger.info(f"✅ Bot retrieved: @{bot_username} (Telegram ID: {telegram_bot_id})")
        except Exception as e:
            logger.error(f"Could not get bot info: {e}")
            bot_username = "Noma'lum"

        # Check if bot is admin in channel
        try:
            if telegram_bot_id:
                member = await temp_bot.get_chat_member(channel_id, telegram_bot_id)
                is_admin = member.status in ["administrator", "creator"]
                logger.info(f"Admin check: {is_admin}")
        except Exception as e:
            logger.warning(f"Could not check admin status: {e}")
            admin_check_failed = True

        await temp_bot.session.close()

    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        admin_check_failed = True

    # Send notification to manager (ADMIN_ID)
    client_name = callback.from_user.full_name or "Noma'lum"
    client_username = callback.from_user.username or "Noma'lum"

    manager_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Botni tasdiqlash", callback_data=f"mgr_approve_bot_{bot_id}")],
        [InlineKeyboardButton(text="🛑 Botni to'xtatish", callback_data=f"mgr_stop_bot_{bot_id}")]
    ])

    manager_msg = (
        f"🆕 <b>Yangi bot yaratildi!</b>\n\n"
        f"👤 Client: <b>{client_name}</b>\n"
        f"📱 Username: @{client_username}\n"
        f"🆔 User ID: <code>{user_id}</code>\n\n"
        f"🤖 Bot nomi: <b>{data['bot_username']}</b>\n"
        f"� Bot username: @{bot_username or 'Noma\'lum'}\n"
        f"📺 Kanal ID: <code>{data['channel_link']}</code>\n"
        f"💰 Tarif: <b>{'Premium' if data['plan'] == 'premium' else 'Free'}</b>\n"
        f"🔐 Admin: <b>{'Ha ✅' if is_admin else 'Yo\'q ❌'}</b>\n"
    )

    try:
        await bot_instance.send_message(
            chat_id=settings.ADMIN_ID[0],
            text=manager_msg,
            reply_markup=manager_keyboard,
            parse_mode="HTML"
        )
        logger.info(f"📨 Manager notified about new bot: {data['bot_username']}")
    except Exception as notify_error:
        logger.error(f"❌ Manager notification error: {notify_error}")

    # Get language from state
    lang = data.get("lang", "uz")

    # Translations for success message
    success_titles = {
        "uz": "✅ <b>Bot muvaffaqiyatli yaratildi!</b>",
        "ru": "✅ <b>Бот успешно создан!</b>",
        "en": "✅ <b>Bot created successfully!</b>"
    }
    bot_username_label = {"uz": "🤖 Bot username", "ru": "🤖 Юзернейм бота", "en": "🤖 Bot username"}
    plan_label = {"uz": "💰 Tarif", "ru": "💰 Тариф", "en": "💰 Plan"}
    status_label = {"uz": "📊 Holati", "ru": "📊 Статус", "en": "📊 Status"}
    status_active = {"uz": "Faol", "ru": "Активен", "en": "Active"}
    plan_names = {"uz": {"premium": "Premium", "free": "Free"}, "ru": {"premium": "Премиум", "free": "Бесплатный"}, "en": {"premium": "Premium", "free": "Free"}}
    unknown = {"uz": "Noma'lum", "ru": "Неизвестно", "en": "Unknown"}

    success_msg = (
        f"{success_titles.get(lang, success_titles['uz'])}\n\n"
        f"{bot_username_label.get(lang, bot_username_label['uz'])}: <b>@{data['bot_username']}</b>\n"
        f"{plan_label.get(lang, plan_label['uz'])}: <b>{plan_names.get(lang, plan_names['uz']).get(data['plan'], 'Free')}</b>\n"
        f"{status_label.get(lang, status_label['uz'])}: <b>{status_active.get(lang, 'Active')}</b>\n"
    )

    # Add admin warning if not admin or check failed
    admin_warning_texts = {
        "uz": "\n⚠️ <b>OGOHLANTIRISH!</b>\nBot kanalda <b>ADMIN EMAS</b>!\nUni admin qilib, /start ni qayta bosing.",
        "ru": "\n⚠️ <b>ВНИМАНИЕ!</b>\nБот <b>НЕ АДМИН</b> в канале!\nДобавьте его администратором и нажмите /start.",
        "en": "\n⚠️ <b>WARNING!</b>\nBot is <b>NOT ADMIN</b> in channel!\nMake it admin and press /start again."
    }
    admin_ok_texts = {
        "uz": "\n✅ Bot kanalda admin sifatida qo'shilgan",
        "ru": "\n✅ Бот добавлен как администратор канала",
        "en": "\n✅ Bot is added as channel admin"
    }

    if admin_check_failed or not is_admin:
        success_msg += admin_warning_texts.get(lang, admin_warning_texts['uz'])
    else:
        success_msg += admin_ok_texts.get(lang, admin_ok_texts['uz'])

    # Add balance info if premium
    if data['plan'] == 'premium':
        premium_deducted = {"uz": "\n💳 Premium balansdan yechildi", "ru": "\n💳 Списано с баланса за Премиум", "en": "\n💳 Premium deducted from balance"}
        success_msg += premium_deducted.get(lang, premium_deducted['uz'])

    main_menu_hint = {"uz": "\n\nBosh menyudan /start bosing.", "ru": "\n\nНажмите /start для главного меню.", "en": "\n\nPress /start for main menu."}
    success_msg += main_menu_hint.get(lang, main_menu_hint['uz'])

    await callback.message.edit_text(
        success_msg,
        parse_mode="HTML"
    )

    # Send warning message with check button if not admin
    if admin_check_failed or not is_admin:
        check_btn_text = {"uz": "🔍 Tekshirish", "ru": "🔍 Проверить", "en": "🔍 Check"}
        check_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=check_btn_text.get(lang, check_btn_text['uz']), callback_data=f"check_bot_admin_{bot_id}")],
        ])

        bot_display = bot_username or unknown.get(lang, "Unknown")
        channel_display = data['channel_link']

        warning_msgs = {
            "uz": f"⚠️ <b>OGOHLANTIRISH!</b>\n\n🤖 Bot: @{bot_display}\n📢 Kanal: {channel_display}\n\nBot kanalda <b>ADMIN EMAS</b>!\n\nBot to'g'ri ishlashi uchun:\n1. @BotFather dan yuborilgan bot linki orqali kanalga qo'shing\n2. Botni <b>ADMIN</b> qiling\n3. Quyidagi \"Tekshirish\" tugmasini bosing",
            "ru": f"⚠️ <b>ВНИМАНИЕ!</b>\n\n🤖 Бот: @{bot_display}\n📢 Канал: {channel_display}\n\nБот <b>НЕ АДМИН</b> в канале!\n\nДля работы бота:\n1. Добавьте бота в канал через ссылку от @BotFather\n2. Сделайте бота <b>АДМИНОМ</b>\n3. Нажмите кнопку \"Проверить\" ниже",
            "en": f"⚠️ <b>WARNING!</b>\n\n🤖 Bot: @{bot_display}\n📢 Channel: {channel_display}\n\nBot is <b>NOT ADMIN</b> in channel!\n\nFor bot to work:\n1. Add bot to channel via @BotFather link\n2. Make bot an <b>ADMIN</b>\n3. Press \"Check\" button below"
        }

        await callback.message.answer(
            warning_msgs.get(lang, warning_msgs['uz']),
            reply_markup=check_keyboard,
            parse_mode="HTML"
        )

    await state.clear()
    await callback.answer()


@router.callback_query(BotCreationStates.confirming_terms, F.data == "cancel_creation")
async def cancel_creation(callback: CallbackQuery, state: FSMContext) -> None:
    """Cancel bot creation"""
    user_id = callback.from_user.id
    data = await state.get_data()
    lang = data.get("lang", "uz")

    async with AsyncSessionLocal() as session:
        from app.crud import create_client_bot
        try:
            # Update client - terms = False, save other data
            client = await get_client_by_user_id(session, user_id)
            if client:
                client.terms = False
                client.plan_type = data['plan']
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            client.plan_start_date = now
            if data['plan'] != 'free':
                client.plan_end_date = now + datetime.timedelta(days=30)
                client.phone_number = data['phone']

            # Create bot with inactive status
            bot = await create_client_bot(
                session,
                user_id=user_id,
                bot_username=data['bot_username'],
                bot_token=data['bot_token'],
                channel_id=int(data['channel_link']),
                card_number=data['card_number'],
                oy_narx=data['oy_narx'],
                yil_narx=data['yil_narx'],
                cheksiz_narx=data['cheksiz_narx'],
                status="inactive"
            )
        except Exception as e:
            pass

    cancel_msgs = {
        "uz": "❌ Bot yaratish bekor qilindi.\n\n/start bosing bosh menyuga qaytish uchun.",
        "ru": "❌ Создание бота отменено.\n\nНажмите /start для возврата в главное меню.",
        "en": "❌ Bot creation cancelled.\n\nPress /start to return to main menu."
    }

    await callback.message.edit_text(cancel_msgs.get(lang, cancel_msgs['uz']))
    await state.clear()
    await callback.answer()


# ==================== Manager Callbacks ====================

@router.callback_query(F.data.startswith("mgr_approve_bot_"))
async def manager_approve_bot(callback: CallbackQuery) -> None:
    """Manager approves the bot - just confirm, no action needed"""
    import logging
    logger = logging.getLogger(__name__)

    # Check if user is admin
    if callback.from_user.id not in settings.ADMIN_ID:
        await callback.answer("❌ Sizda bu amalni bajarish huquqi yo'q!", show_alert=True)
        return

    bot_id = int(callback.data.split("_")[-1])

    async with AsyncSessionLocal() as session:
        bot = await get_bot_by_id(session, bot_id)
        if bot:
            bot_username = bot.bot_username
            # Update message to show approved
            await callback.message.edit_text(
                callback.message.text + f"\n\n✅ <b>Tasdiqlandi</b> - Bot ishlayapti",
                parse_mode="HTML"
            )
            logger.info(f"✅ Manager approved bot: {bot_username} (ID: {bot_id})")
        else:
            await callback.message.edit_text(
                callback.message.text + f"\n\n⚠️ Bot topilmadi",
                parse_mode="HTML"
            )

    await callback.answer("✅ Bot tasdiqlandi!")


@router.callback_query(F.data.startswith("mgr_stop_bot_"))
async def manager_stop_bot(callback: CallbackQuery) -> None:
    """Manager stops the bot - set should_stop flag in database"""
    import logging
    logger = logging.getLogger(__name__)

    # Check if user is admin
    if callback.from_user.id not in settings.ADMIN_ID:
        await callback.answer("❌ Sizda bu amalni bajarish huquqi yo'q!", show_alert=True)
        return

    bot_id = int(callback.data.split("_")[3])

    async with AsyncSessionLocal() as session:
        from app.crud.bot_crud import get_bot_by_id, set_bot_stop_flag
        bot = await get_bot_by_id(session, bot_id)
        if not bot:
            await callback.answer("❌ Bot topilmadi!", show_alert=True)
            return

        bot_username = bot.bot_username

        # Set should_stop = True (daemon will handle stopping)
        await set_bot_stop_flag(session, bot_id, True)
        logger.info(f"🛑 should_stop flag set for bot: {bot_username} (ID: {bot_id})")

        # Shuningdek, xotiradagi taskni ham to'xtatamiz
        from app.bot_manager import stop_bot_task
        stop_bot_task(bot.bot_token)

        # Update message to show stopping
        await callback.message.edit_text(
            callback.message.text + f"\n\n🛑 <b>To'xtatilmoqda...</b> - Bot tez orada to'xtatiladi",
            parse_mode="HTML"
        )
        logger.info(f"🛑 Manager requested stop for bot: {bot_username} (ID: {bot_id})")

    await callback.answer("🛑 Bot to'xtatish buyrug'i yuborildi!")


@router.callback_query(F.data.startswith("check_bot_admin_"))
async def check_bot_admin(callback: CallbackQuery) -> None:
    """Check if bot is admin in channel - re-verify"""
    import asyncio
    
    try:
        # Parse callback data - just bot_id
        parts = callback.data.split("_")
        logger.info(f"Callback data parts: {parts}")
        bot_id = int(parts[3])
        logger.info(f"Bot ID extracted: {bot_id}")
        
        # Get bot details from database
        async with AsyncSessionLocal() as session:
            from app.crud import get_bot_by_id
            bot_from_db = await get_bot_by_id(session, bot_id)
            logger.info(f"Bot from DB: {bot_from_db}")
            
            if not bot_from_db:
                logger.error(f"Bot not found in database: {bot_id}")
                await callback.answer("❌ Bot topilmadi", show_alert=True)
                return
            
            bot_token = bot_from_db.bot_token
            channel_id = int(bot_from_db.channel_id) if isinstance(bot_from_db.channel_id, str) else bot_from_db.channel_id
            bot_username = bot_from_db.bot_username
            logger.info(f"Bot details - Name: {bot_username}, Channel: {channel_id} (type: {type(channel_id).__name__})")
        
        # Check admin status
        is_admin = False
        bot_username = None
        temp_bot = None
        
        try:
            temp_bot = Bot(token=bot_token)
            logger.info(f"Bot instance created for token: {bot_token[:20]}...")
            
            # Get bot info
            try:
                bot_info = await temp_bot.get_me()
                bot_username = bot_info.username
                bot_api_id = bot_info.id
                logger.info(f"Bot info retrieved - Username: @{bot_username}, ID: {bot_api_id}")
            except Exception as e:
                logger.error(f"Error getting bot info: {e}")
                await callback.answer(f"❌ Bot tekshirilmadi: {e}", show_alert=True)
                if temp_bot:
                    await temp_bot.session.close()
                return
            
            # Check admin status
            try:
                logger.info(f"Checking admin status in channel {channel_id} for bot {bot_api_id}")
                member = await temp_bot.get_chat_member(channel_id, bot_api_id)
                is_admin = member.status in ["administrator", "creator"]
                logger.info(f"Admin check result: {is_admin} (status: {member.status})")
            except Exception as e:
                logger.warning(f"Could not check admin status: {e}")
                # Bot is not a member - not admin
                is_admin = False
            
            if temp_bot:
                await temp_bot.session.close()
        except Exception as e:
            logger.error(f"Error in check_bot_admin: {e}")
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
            if temp_bot:
                try:
                    await temp_bot.session.close()
                except:
                    pass
            return
        
        # If admin verified - update message and notify manager
        if is_admin:
            logger.info(f"Bot {bot_id} is admin - updating message and notifying manager")
            # Update the warning message
            try:
                await callback.message.edit_text(
                    f"✅ <b>Bot tasdiqlandi!</b>\n\n"
                    f"🤖 Bot: @{bot_username}\n"
                    f"📢 Kanal: {channel_id}\n\n"
                    f"Bot kanalda admin sifatida qo'shilgan! ✅\n\n"
                    f"Endi bot to'g'ri ishlaydi."
                )
            except Exception as e:
                logger.error(f"Error updating message: {e}")
            
            # Create manager invite link if not exists
            manager_invite_link = None
            try:
                temp_bot_for_link = Bot(token=bot_token)
                invite = await temp_bot_for_link.create_chat_invite_link(
                    channel_id,
                    name="Manager Access",
                    creates_join_request=False
                )
                manager_invite_link = invite.invite_link
                logger.info(f"✅ Manager invite link created: {manager_invite_link}")
                await temp_bot_for_link.session.close()
            except Exception as e:
                logger.warning(f"⚠️ Could not create manager invite link: {str(e)}")
                manager_invite_link = None
            
            # Get bot info from database and update with link
            async with AsyncSessionLocal() as session:
                from app.crud import get_bot_by_id, update_bot_info
                bot_from_db = await get_bot_by_id(session, bot_id)
                if bot_from_db:
                    user_id = bot_from_db.user_id
                    bot_username = bot_from_db.bot_username
                    
                    # Update with the newly created link if it didn't exist
                    if manager_invite_link and not bot_from_db.manager_invite_link:
                        await update_bot_info(
                            session,
                            bot_token,
                            manager_invite_link=manager_invite_link
                        )
                        logger.info(f"Manager invite link saved to database for bot {bot_id}")
                    else:
                        manager_invite_link = bot_from_db.manager_invite_link
                    
                    logger.info(f"Bot {bot_username} verified as admin - no duplicate manager notification sent")
                else:
                    logger.error(f"Bot not found in database during notification: {bot_id}")
            
            await callback.answer("✅ Bot tasdiqlandi!", show_alert=True)
        else:
            # Still not admin
            logger.warning(f"Bot {bot_id} is still not admin")
            try:
                await callback.message.edit_text(
                    f"❌ <b>Bot hali ham ADMIN EMAS!</b>\n\n"
                    f"🤖 Bot: @{bot_username or 'Noma\'lum'}\n"
                    f"📢 Kanal: {channel_id}\n\n"
                    f"Iltimos qayta urinib ko'ring:\n"
                    f"1. Botni kanalga admin sifatida qo'shing\n"
                    f"2. Qayta tekshirish tugmasini bosing",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 Qayta tekshirish", callback_data=f"check_bot_admin_{bot_id}")],
                    ])
                )
            except Exception as e:
                logger.error(f"Error updating message for not admin case: {e}")
            await callback.answer("❌ Bot hali ham admin emas", show_alert=True)
    
    except Exception as e:
        logger.exception(f"Unexpected error in check_bot_admin: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

@router.callback_query(F.data == "toggle_auto_renew")
async def toggle_auto_renew_callback(callback: CallbackQuery) -> None:
    """Toggle the auto-renew feature in settings"""
    user_id = callback.from_user.id
    
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        if not client:
            return
            
        # Toggle
        client.oylik_obuna = not client.oylik_obuna
        await session.commit()
        
        lang = client.language or "uz"
        
        # Determine language translations specifically for settings update
        status = "🟢 Yoqilgan" if client.oylik_obuna else "🔴 O'chirilgan"
        lang_text = "O'zbekcha" if lang == "uz" else "Русский" if lang == "ru" else "English"
        
        if lang == "ru":
            text = "⚙️ <b>Настройки</b>\n\nВыберите, что хотите изменить:"
            status = "🟢 Включена" if client.oylik_obuna else "🔴 Отключена"
            btn_auto = f"🔄 Авто-оплата: {status}"
            btn_lang = f"🌐 Язык: {lang_text}"
        elif lang == "en":
            text = "⚙️ <b>Settings</b>\n\nChoose what to change:"
            status = "🟢 Enabled" if client.oylik_obuna else "🔴 Disabled"
            btn_auto = f"🔄 Auto-renew: {status}"
            btn_lang = f"🌐 Language: {lang_text}"
        else:
            text = "⚙️ <b>Sozlamalar</b>\n\nQuyidagilardan birini tanlang:"
            btn_auto = f"🔄 Avto to'lov: {status}"
            btn_lang = f"🌐 Til: {lang_text}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=btn_auto, callback_data="toggle_auto_renew")],
            [InlineKeyboardButton(text=btn_lang, callback_data="cmd_lang_trigger")]
        ])
        
        try:
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except:
            pass # Unchanged message exception catch
            
    await callback.answer("Avto to'lov o'zgartirildi =)")

@router.callback_query(F.data == "cmd_lang_trigger")
async def cmd_lang_trigger_callback(callback: CallbackQuery) -> None:
    """Trigger language selection from settings menu"""
    from app.translations import get_language_keyboard
    lang_buttons = get_language_keyboard()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=lang_buttons[0]["text"], callback_data=lang_buttons[0]["callback_data"])],
        [InlineKeyboardButton(text=lang_buttons[1]["text"], callback_data=lang_buttons[1]["callback_data"])],
        [InlineKeyboardButton(text=lang_buttons[2]["text"], callback_data=lang_buttons[2]["callback_data"])],
    ])
    text = "Kerakli tilni tanlang:\nВыберите нужный язык:\nChoose your language:"
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

