"""
Start command handler - User welcome and Admin panel
"""
from aiogram import F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import text
from app.database import AsyncSessionLocal
from client_bot.config import logger, REKLAMA_TEXT
from client_bot.utils.database import get_or_create_user, get_bot_info, get_client_plan_and_ads
from locales import get_text as get_admin_text
from client_bot.states import LanguageStates


def register_start_handlers(dp, bot, owner_id: int, bot_username: str, bot_token: str, bot_db_id: int):
    """Register /start command handler"""

    @dp.message(Command("start"))
    async def cmd_start(message: Message, state: FSMContext):
        user_id = message.from_user.id
        username = message.from_user.username
        name = message.from_user.first_name or "User"

        logger.info(f"/start from {user_id} (@{username})")

        # Clear all states and remove buttons
        await state.clear()

        # Check if user is the bot owner (admin)
        if user_id == owner_id:
            await show_admin_panel(message, owner_id, bot_token, bot_db_id)
            return

        # Check user's current language - show selection if new user (per-bot)
        async with AsyncSessionLocal() as session:
            check_query = text("SELECT language FROM users WHERE user_id = :user_id AND bot_id = :bot_id")
            result = await session.execute(check_query, {"user_id": user_id, "bot_id": bot_db_id})
            existing_user = result.fetchone()

            is_new_user = existing_user is None
            current_lang = existing_user[0] if existing_user and existing_user[0] else 'uz'

        # If new user, show language selection
        if is_new_user:
            await show_language_selection(message, state)
            return

        # Save/update existing user in database
        async with AsyncSessionLocal() as session:
            try:
                user = await get_or_create_user(
                    session=session,
                    admin_id=owner_id,
                    user_id=user_id,
                    bot_id=bot_db_id,
                    username=username,
                    name=name
                )
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")

        # Show welcome with their language
        await show_welcome_message(message, owner_id, bot_username, current_lang, bot_token)

    @dp.callback_query(F.data.startswith("lang_"))
    async def select_language(callback, state: FSMContext):
        """Handle language selection"""
        user_id = callback.from_user.id
        username = callback.from_user.username
        name = callback.from_user.first_name or "User"
        lang = callback.data.split("_")[1]  # Extract language code

        # Save user with selected language
        async with AsyncSessionLocal() as session:
            try:
                user = await get_or_create_user(
                    session=session,
                    admin_id=owner_id,
                    user_id=user_id,
                    bot_id=bot_db_id,
                    username=username,
                    name=name
                )

                # Update language (per-bot)
                update_query = text("""
                    UPDATE users
                    SET language = :lang
                    WHERE user_id = :user_id AND bot_id = :bot_id
                """)
                await session.execute(update_query, {"user_id": user_id, "bot_id": bot_db_id, "lang": lang})
                await session.commit()
                logger.info(f"Language set to {lang} for user {user_id} in bot {bot_db_id}")
            except Exception as e:
                logger.error(f"Error saving language: {e}")

        # Clear state and show welcome message in selected language
        await state.clear()
        await callback.answer(get_admin_text("language_selected", lang))

        # Edit message to show welcome
        await show_welcome_message(callback.message, owner_id, bot_username, lang, bot_token)


async def show_language_selection(message: Message, state: FSMContext):
    """Show language selection keyboard"""
    await state.set_state(LanguageStates.selecting_language)

    greeting_text = (
        "Assalomu alaykum! \n\n"
        "Привет! \n\n"
        "Hello! \n\n"
        "<b>Iltimos, til tanlang / Выберите язык / Please select language:</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text="English", callback_data="lang_en")
        ]
    ])

    await message.answer(greeting_text, parse_mode="HTML", reply_markup=keyboard)


async def show_welcome_message(message: Message, owner_id: int, bot_username: str, lang: str, bot_token: str):
    """Show welcome message in selected language"""
    # Get bot info and user plan
    bot_info = None
    client_plan = 'free'
    ads_enabled = True

    async with AsyncSessionLocal() as session:
        try:
            bot_info = await get_bot_info(session, bot_token)
            client_plan, ads_enabled = await get_client_plan_and_ads(session, owner_id)
            logger.info(f"Client plan: {client_plan}, Ads Enabled: {ads_enabled}")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")

    # Translations for welcome message
    welcome_texts = {
        "uz": {
            "greeting": f"Assalomu alaykum, {message.from_user.first_name or 'User'}!",
            "welcome": f"<b>{bot_username}</b> botiga xush kelibsiz!",
            "select_duration": "<b>Telegram kanalga a'zo bo'lish uchun muddatni tanlang:</b>",
            "test": "Test - 2 daqiqa (Bepul)",
            "monthly": "Oylik",
            "yearly": "Yillik",
            "unlimited": "Cheksiz",
            "topup": "Hisobni to'ldirish"
        },
        "ru": {
            "greeting": f"Привет, {message.from_user.first_name or 'User'}!",
            "welcome": f"Добро пожаловать в бот <b>{bot_username}</b>!",
            "select_duration": "<b>Выберите продолжительность подписки на канал:</b>",
            "test": "Тест - 2 минуты (Бесплатно)",
            "monthly": "Месячная",
            "yearly": "Годовая",
            "unlimited": "Неограниченная",
            "topup": "Пополнить баланс"
        },
        "en": {
            "greeting": f"Hello, {message.from_user.first_name or 'User'}!",
            "welcome": f"Welcome to <b>{bot_username}</b> bot!",
            "select_duration": "<b>Select subscription duration for the channel:</b>",
            "test": "Test - 2 minutes (Free)",
            "monthly": "Monthly",
            "yearly": "Yearly",
            "unlimited": "Unlimited",
            "topup": "Top up balance"
        }
    }

    texts = welcome_texts.get(lang, welcome_texts["uz"])

    # Build welcome message
    welcome_msg = f"{texts['greeting']}\n\n"
    welcome_msg += f"{texts['welcome']}\n\n"

    # Create plan selection keyboard
    keyboard_buttons = []

    if bot_info:
        welcome_msg += f"{texts['select_duration']}\n\n"

        keyboard_buttons.append([InlineKeyboardButton(
            text=texts['test'],
            callback_data="plan_test_2min"
        )])

        if bot_info.get('oy_narx'):
            price = float(bot_info['oy_narx'])
            welcome_msg += f"{texts['monthly']}: {price:,.0f} so'm\n"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{texts['monthly']} - {price:,.0f} so'm",
                callback_data="plan_monthly"
            )])

        if bot_info.get('yil_narx'):
            price = float(bot_info['yil_narx'])
            welcome_msg += f"{texts['yearly']}: {price:,.0f} so'm\n"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{texts['yearly']} - {price:,.0f} so'm",
                callback_data="plan_yearly"
            )])

        if bot_info.get('cheksiz_narx'):
            price = float(bot_info['cheksiz_narx'])
            welcome_msg += f"{texts['unlimited']}: {price:,.0f} so'm\n"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"{texts['unlimited']} - {price:,.0f} so'm",
                callback_data="plan_unlimited"
            )])

    # Add balance button
    keyboard_buttons.append([InlineKeyboardButton(
        text=texts['topup'],
        callback_data="topup_balance"
    )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    # Add REKLAMA_TEXT if required by plan or user toggle
    if client_plan == 'free' or ads_enabled:
        welcome_msg += f"\n\n<i>{REKLAMA_TEXT}</i>"

    # Send welcome message
    await message.answer(welcome_msg, parse_mode="HTML", reply_markup=keyboard)



async def show_admin_panel(message: Message, owner_id: int, bot_token: str, bot_db_id: int):
    """Show admin panel for bot owner"""
    from client_bot.utils.database import get_client_language

    async with AsyncSessionLocal() as session:
        try:
            # Get client language
            lang = await get_client_language(session, owner_id)

            # Get bot info
            bot_info = await get_bot_info(session, bot_token)

            # Get statistics (per-bot)
            total_query = text("SELECT COUNT(*) FROM users WHERE admin_id = :admin_id AND bot_id = :bot_id")
            total_result = await session.execute(total_query, {"admin_id": owner_id, "bot_id": bot_db_id})
            total_users = total_result.scalar() or 0

            active_query = text("SELECT COUNT(*) FROM users WHERE admin_id = :admin_id AND bot_id = :bot_id AND status = 'active'")
            active_result = await session.execute(active_query, {"admin_id": owner_id, "bot_id": bot_db_id})
            active_users = active_result.scalar() or 0

            removed_query = text("SELECT COUNT(*) FROM users WHERE admin_id = :admin_id AND bot_id = :bot_id AND status = 'removed'")
            removed_result = await session.execute(removed_query, {"admin_id": owner_id, "bot_id": bot_db_id})
            removed_users = removed_result.scalar() or 0

            revenue_query = text("""
                SELECT COALESCE(SUM(amount), 0) FROM transactions
                WHERE admin_id = :admin_id AND role = 'plan_purchase' AND status = 'approved'
            """)
            revenue_result = await session.execute(revenue_query, {"admin_id": owner_id})
            total_revenue = float(revenue_result.scalar() or 0)

        except Exception as e:
            logger.error(f"Stats error: {e}")
            total_users = 0
            active_users = 0
            removed_users = 0
            total_revenue = 0
            bot_info = None
            lang = "uz"

    # Build admin panel with translations
    currency = get_admin_text("currency", lang)

    admin_msg = f"{get_admin_text('admin_panel_title', lang)}\n\n"

    if bot_info:
        admin_msg += f"{get_admin_text('bot_label', lang)} {bot_info.get('bot_username', 'N/A')}\n"
        admin_msg += f"{get_admin_text('channel_id_label', lang)} {bot_info.get('channel_id', 'N/A')}\n\n"

    admin_msg += f"{get_admin_text('short_stats', lang)}\n"
    admin_msg += f"  {get_admin_text('total_users_label', lang)}: {total_users}\n"
    admin_msg += f"  {get_admin_text('active_label', lang)}: {active_users}\n"
    admin_msg += f"  {get_admin_text('removed_label', lang)}: {removed_users}\n"
    admin_msg += f"  {get_admin_text('revenue_label', lang)}: {total_revenue:,.0f} {currency}\n"

    # Admin keyboard with translations
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_admin_text("btn_stats", lang), callback_data="admin_stats")],
        [
            InlineKeyboardButton(text=get_admin_text("btn_users_excel", lang), callback_data="admin_users_excel"),
            InlineKeyboardButton(text=get_admin_text("btn_payments_excel", lang), callback_data="admin_payments_excel")
        ],
        [
            InlineKeyboardButton(text=get_admin_text("btn_active_users", lang), callback_data="admin_active_users"),
            InlineKeyboardButton(text=get_admin_text("btn_removed_users", lang), callback_data="admin_removed_users")
        ]
    ])

    await message.answer(admin_msg, parse_mode="HTML", reply_markup=admin_keyboard)
