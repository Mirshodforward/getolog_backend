from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from app.states import BotCreationStates, BotEditStates
from app.database import AsyncSessionLocal
from app.crud import get_client_by_user_id, get_bot_by_token

router = Router()


# Translation dictionaries for message handler
MSGS = {
    "contact_required": {
        "uz": "❌ Iltimos, kontakt tugmasini bosing!",
        "ru": "❌ Пожалуйста, нажмите кнопку контакта!",
        "en": "❌ Please press the contact button!"
    },
    "invalid_phone": {
        "uz": "❌ Noto'g'ri telefon raqami! Iltimos, qayta yo'llang.",
        "ru": "❌ Неверный номер телефона! Попробуйте снова.",
        "en": "❌ Invalid phone number! Please try again."
    },
    "enter_bot_name": {
        "uz": "🤖 Bot nomini kiriting:\n\nMasalan: Birinchi Bot, kurs_bot, bot123",
        "ru": "🤖 Введите название бота:\n\nНапример: Первый Бот, kurs_bot, bot123",
        "en": "🤖 Enter bot name:\n\nExample: First Bot, kurs_bot, bot123"
    },
    "bot_name_short": {
        "uz": "❌ Bot nomi juda qisqa! Iltimos, 2 harfdan uzun nom kiriting.",
        "ru": "❌ Название слишком короткое! Введите минимум 2 символа.",
        "en": "❌ Bot name is too short! Please enter at least 2 characters."
    },
    "enter_token": {
        "uz": "🔑 Bot tokenini kiriting:\n\n1. @BotFather orqali /newbot komandasi yordamida bot yarating\n2. So'ngra BotFatherdan bot tokenini oling\n3. Quyidagi formatda tokenni kiriting:\n\nMisol: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ",
        "ru": "🔑 Введите токен бота:\n\n1. Создайте бота через @BotFather командой /newbot\n2. Получите токен от BotFather\n3. Введите токен в формате:\n\nПример: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ",
        "en": "🔑 Enter bot token:\n\n1. Create a bot via @BotFather with /newbot command\n2. Get the token from BotFather\n3. Enter the token in format:\n\nExample: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ"
    },
    "invalid_token": {
        "uz": "❌ Noto'g'ri token!\n\n@BotFather dan olgan tokeningizni tekshiring va qayta jo'nating.",
        "ru": "❌ Неверный токен!\n\nПроверьте токен от @BotFather и отправьте снова.",
        "en": "❌ Invalid token!\n\nCheck your token from @BotFather and try again."
    },
    "token_already_exists": {
        "uz": "⚠️ Bu token allaqachon tizimda mavjud!\n\nIltimos, boshqa bot tokeni kiriting yoki @BotFather orqali yangi bot yarating.",
        "ru": "⚠️ Этот токен уже существует в системе!\n\nПожалуйста, введите другой токен бота или создайте нового бота через @BotFather.",
        "en": "⚠️ This token already exists in the system!\n\nPlease enter a different bot token or create a new bot via @BotFather."
    },
    "select_channel_btn": {
        "uz": "📢 Kanalimni tanlash",
        "ru": "📢 Выбрать мой канал",
        "en": "📢 Select my channel"
    },
    "select_channel": {
        "uz": "📢 Endi bot boshqarishi kerak bo'lgan kanalingizni tanlang:\n\nQuyidagi tugmani bosing va kanalingizni tanlang.",
        "ru": "📢 Выберите канал, которым будет управлять бот:\n\nНажмите кнопку ниже и выберите канал.",
        "en": "📢 Select the channel for the bot to manage:\n\nPress the button below and select your channel."
    },
    "channel_required": {
        "uz": "❌ Iltimos, '📢 Kanalimni tanlash' tugmasini bosing va kanalingizni tanlang!",
        "ru": "❌ Пожалуйста, нажмите '📢 Выбрать мой канал' и выберите канал!",
        "en": "❌ Please press '📢 Select my channel' and choose your channel!"
    },
    "channel_accepted": {
        "uz": "✅ Kanal qabul qilindi!\n\n⚠️ <b>MUHIM OGOHLANTIRISH!</b>\n\nSiz @BotFather orqali yaratgan botingizni shu kanalga <b>ADMIN qilishingiz kerak</b>, aks holda bot to'g'ri ishlamaydi!\n\nIltimos hoziroq botingizni kanalingizga admin qiling va quyidagi tugmani bosing.",
        "ru": "✅ Канал принят!\n\n⚠️ <b>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ!</b>\n\nВы должны добавить бота, созданного через @BotFather, <b>АДМИНИСТРАТОРОМ</b> в этот канал, иначе бот не будет работать!\n\nДобавьте бота администратором канала и нажмите кнопку ниже.",
        "en": "✅ Channel accepted!\n\n⚠️ <b>IMPORTANT WARNING!</b>\n\nYou must add the bot created via @BotFather as an <b>ADMIN</b> to this channel, otherwise the bot won't work!\n\nPlease add your bot as admin now and press the button below."
    },
    "understood_btn": {
        "uz": "✅ Tushundim",
        "ru": "✅ Понял",
        "en": "✅ Understood"
    },
    "press_button": {
        "uz": "❌ Iltimos, tugmani bosing!",
        "ru": "❌ Пожалуйста, нажмите кнопку!",
        "en": "❌ Please press the button!"
    },
    "invalid_card": {
        "uz": "❌ Noto'g'ri karta raqami! 16 raqam bo'lishi kerak.",
        "ru": "❌ Неверный номер карты! Должно быть 16 цифр.",
        "en": "❌ Invalid card number! Must be 16 digits."
    },
    "prices_intro": {
        "uz": "Botingizda 3ta ta'rif mavjud.\n\nNarxlarni navbat bilan kiriting:\nOylik - (1 oy)\nYillik - (12 oy)\nCheksiz - (cheklanmagan muddat)\n\n💰 Oylik narxni kiriting (so'm, masalan: 50000):",
        "ru": "В вашем боте 3 тарифа.\n\nВведите цены по очереди:\nМесячный - (1 месяц)\nГодовой - (12 месяцев)\nБезлимит - (без ограничений)\n\n💰 Введите месячную цену (сум, например: 50000):",
        "en": "Your bot has 3 pricing plans.\n\nEnter prices one by one:\nMonthly - (1 month)\nYearly - (12 months)\nUnlimited - (no time limit)\n\n💰 Enter monthly price (UZS, e.g.: 50000):"
    },
    "invalid_price": {
        "uz": "❌ Noto'g'ri raqam! Iltimos, to'g'ri narxni kiriting.",
        "ru": "❌ Неверное число! Введите корректную цену.",
        "en": "❌ Invalid number! Please enter a valid price."
    },
    "enter_yearly": {
        "uz": "💰 Yillik narxni kiriting (so'm, masalan: 500000):",
        "ru": "💰 Введите годовую цену (сум, например: 500000):",
        "en": "💰 Enter yearly price (UZS, e.g.: 500000):"
    },
    "enter_unlimited": {
        "uz": "💰 Cheksiz (unlimited) narxni kiriting (so'm, masalan: 1000000):",
        "ru": "💰 Введите безлимитную цену (сум, например: 1000000):",
        "en": "💰 Enter unlimited price (UZS, e.g.: 1000000):"
    },
    "summary": {
        "uz": "📋 <b>Qayta ko'rib chiqing</b>\n\n🤖 Bot username: <b>@{bot_username}</b>\n💰 Tarif: <b>{plan}</b>\n📱 Tel: <b>{phone}</b>\n📢 Kanal ID: <b>{channel}</b>\n💳 Karta: <b>****{card}</b>\n\n📊 <b>Narxlar:</b>\n  • Oylik: <b>{monthly:,.0f} so'm</b>\n  • Yillik: <b>{yearly:,.0f} so'm</b>\n  • Cheksiz: <b>{unlimited:,.0f} so'm</b>\n\nSiz quyidagi ✅ Tasdiqlash tugmasini bosish orqali <b>Terms of Service</b> shartlarni qabul qilasiz.",
        "ru": "📋 <b>Проверьте данные</b>\n\n🤖 Username бота: <b>@{bot_username}</b>\n💰 Тариф: <b>{plan}</b>\n📱 Тел: <b>{phone}</b>\n📢 ID канала: <b>{channel}</b>\n💳 Карта: <b>****{card}</b>\n\n📊 <b>Цены:</b>\n  • Месяц: <b>{monthly:,.0f} сум</b>\n  • Год: <b>{yearly:,.0f} сум</b>\n  • Безлимит: <b>{unlimited:,.0f} сум</b>\n\nНажав ✅ Подтвердить, вы принимаете <b>Условия использования</b>.",
        "en": "📋 <b>Review details</b>\n\n🤖 Bot username: <b>@{bot_username}</b>\n💰 Plan: <b>{plan}</b>\n📱 Phone: <b>{phone}</b>\n📢 Channel ID: <b>{channel}</b>\n💳 Card: <b>****{card}</b>\n\n📊 <b>Prices:</b>\n  • Monthly: <b>{monthly:,.0f} UZS</b>\n  • Yearly: <b>{yearly:,.0f} UZS</b>\n  • Unlimited: <b>{unlimited:,.0f} UZS</b>\n\nBy pressing ✅ Confirm, you accept the <b>Terms of Service</b>."
    },
    "confirm_btn": {
        "uz": "✅ Tasdiqlash",
        "ru": "✅ Подтвердить",
        "en": "✅ Confirm"
    },
    "cancel_btn": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отменить",
        "en": "❌ Cancel"
    },
    "plan_premium": {
        "uz": "Premium",
        "ru": "Премиум",
        "en": "Premium"
    },
    "plan_free": {
        "uz": "Free",
        "ru": "Бесплатный",
        "en": "Free"
    }
}


def get_msg(key: str, lang: str = "uz") -> str:
    """Get message by key and language"""
    if key in MSGS:
        return MSGS[key].get(lang, MSGS[key].get("uz", key))
    return key


@router.message(BotCreationStates.entering_phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Process phone number from contact"""
    from aiogram.types import ReplyKeyboardRemove
    import logging
    logger = logging.getLogger(__name__)

    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    logger.info(f"📱 process_phone: user_id={message.from_user.id}, has_contact={message.contact is not None}, state_data={data}")

    if not message.contact:
        await message.answer(get_msg("contact_required", lang))
        return

    # Get phone number from contact
    phone = message.contact.phone_number
    if not phone or len(phone) < 8:
        await message.answer(get_msg("invalid_phone", lang))
        return

    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        # Update client with phone number
        client = await get_client_by_user_id(session, user_id)
        if client:
            client.phone_number = phone
            await session.commit()

    await state.update_data(phone=phone)

    await message.answer(
        get_msg("enter_token", lang),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(BotCreationStates.entering_bot_token)


@router.message(BotCreationStates.entering_bot_token)
async def process_bot_token(message: Message, state: FSMContext) -> None:
    """Process bot token"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    bot_token = message.text.strip()

    if not bot_token or len(bot_token) < 10 or ":" not in bot_token:
        await message.answer(get_msg("invalid_token", lang))
        return

    # Check if token already exists in database
    async with AsyncSessionLocal() as session:
        existing_bot = await get_bot_by_token(session, bot_token)
        if existing_bot:
            await message.answer(get_msg("token_already_exists", lang))
            return

    # Validate token and get bot username
    test_bot = Bot(token=bot_token)
    try:
        bot_info = await test_bot.get_me()
        bot_username = bot_info.username
    except Exception as e:
        await message.answer(get_msg("invalid_token", lang))
        return
    finally:
        await test_bot.session.close()

    await state.update_data(bot_token=bot_token, bot_username=bot_username)

    # Create keyboard with request_chat button
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    from aiogram.types.keyboard_button_request_chat import KeyboardButtonRequestChat

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text=get_msg("select_channel_btn", lang),
                request_chat=KeyboardButtonRequestChat(
                    request_id=1,
                    chat_is_channel=True,
                    bot_is_member=False
                )
            )
        ]],
        resize_keyboard=True
    )

    await message.answer(get_msg("select_channel", lang), reply_markup=keyboard)
    await state.set_state(BotCreationStates.entering_channel_link)


@router.message(BotCreationStates.entering_channel_link)
async def process_channel_link(message: Message, state: FSMContext) -> None:
    """Process shared channel"""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Check if chat was shared
    if not message.chat_shared:
        await message.answer(get_msg("channel_required", lang))
        return

    # Get channel ID from shared chat
    channel_id = message.chat_shared.chat_id

    # Save channel ID instead of link
    await state.update_data(channel_link=str(channel_id))

    # Admin warning
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg("understood_btn", lang), callback_data="admin_understood")],
    ])

    await message.answer(get_msg("channel_accepted", lang), reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(BotCreationStates.admin_warning)


@router.message(BotCreationStates.admin_warning)
async def admin_warning_handler(message: Message, state: FSMContext) -> None:
    """Admin warning handler"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await message.answer(get_msg("press_button", lang))


@router.message(BotCreationStates.entering_card_number)
async def process_card_number(message: Message, state: FSMContext) -> None:
    """Process card number"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    card = message.text.strip().replace(" ", "")

    if not card.isdigit() or len(card) != 16:
        await message.answer(get_msg("invalid_card", lang))
        return

    await state.update_data(card_number=card)

    await message.answer(get_msg("prices_intro", lang), reply_markup=None)
    await state.set_state(BotCreationStates.entering_oy_narx)


@router.message(BotCreationStates.entering_oy_narx)
async def process_oy_narx(message: Message, state: FSMContext) -> None:
    """Process monthly price"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    try:
        oy_narx = float(message.text.strip())
        if oy_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_msg("invalid_price", lang))
        return

    await state.update_data(oy_narx=oy_narx)

    await message.answer(get_msg("enter_yearly", lang))
    await state.set_state(BotCreationStates.entering_yil_narx)


@router.message(BotCreationStates.entering_yil_narx)
async def process_yil_narx(message: Message, state: FSMContext) -> None:
    """Process yearly price"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    try:
        yil_narx = float(message.text.strip())
        if yil_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_msg("invalid_price", lang))
        return

    await state.update_data(yil_narx=yil_narx)

    await message.answer(get_msg("enter_unlimited", lang))
    await state.set_state(BotCreationStates.entering_cheksiz_narx)


@router.message(BotCreationStates.entering_cheksiz_narx)
async def process_cheksiz_narx(message: Message, state: FSMContext) -> None:
    """Process unlimited price"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    try:
        cheksiz_narx = float(message.text.strip())
        if cheksiz_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_msg("invalid_price", lang))
        return

    await state.update_data(cheksiz_narx=cheksiz_narx)

    data = await state.get_data()

    # Plan name translation
    plan_name = get_msg("plan_premium", lang) if data['plan'] == 'premium' else get_msg("plan_free", lang)

    # Show summary
    summary = get_msg("summary", lang).format(
        bot_username=data['bot_username'],
        plan=plan_name,
        phone=data['phone'],
        channel=data['channel_link'],
        card=data['card_number'][-4:],
        monthly=data['oy_narx'],
        yearly=data['yil_narx'],
        unlimited=data['cheksiz_narx']
    )

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_msg("confirm_btn", lang), callback_data="confirm_terms")],
        [InlineKeyboardButton(text=get_msg("cancel_btn", lang), callback_data="cancel_creation")],
    ])

    await message.answer(summary, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(BotCreationStates.confirming_terms)


# ==================== BOT EDIT HANDLERS ====================

# Edit translations
EDIT_MSGS = {
    "invalid_card": {
        "uz": "❌ Noto'g'ri karta raqami! 16 raqam bo'lishi kerak.",
        "ru": "❌ Неверный номер карты! Должно быть 16 цифр.",
        "en": "❌ Invalid card number! Must be 16 digits."
    },
    "invalid_price": {
        "uz": "❌ Noto'g'ri raqam! Iltimos, to'g'ri narxni kiriting.",
        "ru": "❌ Неверное число! Введите корректную цену.",
        "en": "❌ Invalid number! Please enter a valid price."
    },
    "enter_yil": {
        "uz": "💰 Yangi <b>yillik</b> narxni kiriting (so'm):\n\nJoriy narx: <code>{current_price:,.0f}</code> so'm",
        "ru": "💰 Введите новую <b>годовую</b> цену (сум):\n\nТекущая цена: <code>{current_price:,.0f}</code> сум",
        "en": "💰 Enter new <b>yearly</b> price (UZS):\n\nCurrent price: <code>{current_price:,.0f}</code> UZS"
    },
    "enter_cheksiz": {
        "uz": "💰 Yangi <b>cheksiz</b> narxni kiriting (so'm):\n\nJoriy narx: <code>{current_price:,.0f}</code> so'm",
        "ru": "💰 Введите новую <b>безлимитную</b> цену (сум):\n\nТекущая цена: <code>{current_price:,.0f}</code> сум",
        "en": "💰 Enter new <b>unlimited</b> price (UZS):\n\nCurrent price: <code>{current_price:,.0f}</code> UZS"
    },
    "skip_btn": {
        "uz": "⏭ O'tkazib yuborish",
        "ru": "⏭ Пропустить",
        "en": "⏭ Skip"
    },
    "cancel_btn": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отмена",
        "en": "❌ Cancel"
    }
}


def get_edit_msg(key: str, lang: str = "uz", **kwargs) -> str:
    """Get edit message by key and language with formatting"""
    if key in EDIT_MSGS:
        text = EDIT_MSGS[key].get(lang, EDIT_MSGS[key].get("uz", key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    return key


@router.message(BotEditStates.editing_card)
async def process_edit_card(message: Message, state: FSMContext) -> None:
    """Process new card number for edit"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")

    card = message.text.strip().replace(" ", "")

    if not card.isdigit() or len(card) != 16:
        await message.answer(get_edit_msg("invalid_card", lang))
        return

    # Save new card in state
    await state.update_data(new_card=card)

    # Show confirmation screen
    confirm_msg = {
        "uz": f"✅ <b>O'zgarishlar</b>\n\n💳 Yangi karta: <code>{card}</code>\n\n🔄 Botni qayta ishga tushirish uchun <b>Tasdiqlash</b> tugmasini bosing.",
        "ru": f"✅ <b>Изменения</b>\n\n💳 Новая карта: <code>{card}</code>\n\n🔄 Нажмите <b>Подтвердить</b> для перезапуска бота.",
        "en": f"✅ <b>Changes</b>\n\n💳 New card: <code>{card}</code>\n\n🔄 Press <b>Confirm</b> to restart the bot."
    }

    confirm_btn = {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "en": "✅ Confirm"}
    cancel_btn = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=confirm_btn.get(lang, confirm_btn["uz"]), callback_data=f"bot_edit_confirm_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn.get(lang, cancel_btn["uz"]), callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await message.answer(confirm_msg.get(lang, confirm_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.confirming_changes)


@router.message(BotEditStates.editing_oy_narx)
async def process_edit_oy_narx(message: Message, state: FSMContext) -> None:
    """Process new monthly price for edit"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")
    current_yil = data.get("current_yil", 0)

    try:
        oy_narx = float(message.text.strip())
        if oy_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_edit_msg("invalid_price", lang))
        return

    # Save new oy_narx in state
    await state.update_data(new_oy_narx=oy_narx)

    # Move to yil_narx
    skip_btn = get_edit_msg("skip_btn", lang)
    cancel_btn = get_edit_msg("cancel_btn", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_btn, callback_data=f"bot_edit_skip_yil_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn, callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await message.answer(
        get_edit_msg("enter_yil", lang, current_price=current_yil),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.set_state(BotEditStates.editing_yil_narx)


@router.message(BotEditStates.editing_yil_narx)
async def process_edit_yil_narx(message: Message, state: FSMContext) -> None:
    """Process new yearly price for edit"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")
    current_cheksiz = data.get("current_cheksiz", 0)

    try:
        yil_narx = float(message.text.strip())
        if yil_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_edit_msg("invalid_price", lang))
        return

    # Save new yil_narx in state
    await state.update_data(new_yil_narx=yil_narx)

    # Move to cheksiz_narx
    skip_btn = get_edit_msg("skip_btn", lang)
    cancel_btn = get_edit_msg("cancel_btn", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=skip_btn, callback_data=f"bot_edit_skip_cheksiz_{bot_id}")],
        [InlineKeyboardButton(text=cancel_btn, callback_data=f"bot_edit_cancel_{bot_id}")]
    ])

    await message.answer(
        get_edit_msg("enter_cheksiz", lang, current_price=current_cheksiz),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.set_state(BotEditStates.editing_cheksiz_narx)


@router.message(BotEditStates.editing_cheksiz_narx)
async def process_edit_cheksiz_narx(message: Message, state: FSMContext) -> None:
    """Process new unlimited price for edit"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    bot_id = data.get("edit_bot_id")

    try:
        cheksiz_narx = float(message.text.strip())
        if cheksiz_narx <= 0:
            raise ValueError
    except:
        await message.answer(get_edit_msg("invalid_price", lang))
        return

    # Save new cheksiz_narx in state
    await state.update_data(new_cheksiz_narx=cheksiz_narx)

    # Get all data for confirmation
    data = await state.get_data()
    new_oy = data.get("new_oy_narx")
    new_yil = data.get("new_yil_narx")
    current_oy = data.get("current_oy", 0)
    current_yil = data.get("current_yil", 0)

    currency = "so'm" if lang == "uz" else "сум" if lang == "ru" else "UZS"

    oy_display = f"{new_oy:,.0f}" if new_oy else f"{current_oy:,.0f} (o'zgarmadi)" if lang == "uz" else f"{current_oy:,.0f} (без изменений)" if lang == "ru" else f"{current_oy:,.0f} (unchanged)"
    yil_display = f"{new_yil:,.0f}" if new_yil else f"{current_yil:,.0f} (o'zgarmadi)" if lang == "uz" else f"{current_yil:,.0f} (без изменений)" if lang == "ru" else f"{current_yil:,.0f} (unchanged)"
    cheksiz_display = f"{cheksiz_narx:,.0f}"

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

    await message.answer(confirm_msg.get(lang, confirm_msg["uz"]), parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(BotEditStates.confirming_changes)
