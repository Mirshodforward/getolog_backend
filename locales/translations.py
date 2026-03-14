"""
All translations for the Getolog Bot Platform

Languages supported:
- uz: O'zbekcha (Uzbek)
- ru: Русский (Russian)
- en: English

Sections:
1. COMMON - General messages
2. MAIN_MENU - Main menu buttons
3. BOT_CREATION - Bot creation flow
4. MY_BOTS - Bot management
5. BALANCE - Balance and payments
6. ERRORS - Error messages
7. ADMIN - Admin panel messages
8. CLIENT_BOT - Client bot messages
"""

TRANSLATIONS = {
    # ==================== COMMON ====================
    "welcome": {
        "uz": "Assalomu alaykum, {name}! Xush kelibsiz!",
        "ru": "Здравствуйте, {name}! Добро пожаловать!",
        "en": "Hello, {name}! Welcome!"
    },
    "select_language": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Select language:"
    },
    "language_selected": {
        "uz": "Til tanlandi: O'zbekcha",
        "ru": "Язык выбран: Русский",
        "en": "Language selected: English"
    },

    # ==================== MAIN MENU ====================
    "main_menu": {
        "uz": "Asosiy menyu:",
        "ru": "Главное меню:",
        "en": "Main menu:"
    },
    "btn_create_bot": {
        "uz": "Bot yaratish",
        "ru": "Создать бота",
        "en": "Create Bot"
    },
    "btn_my_bots": {
        "uz": "Mening botlarim",
        "ru": "Мои боты",
        "en": "My Bots"
    },

    # ==================== BOT CREATION ====================
    "select_plan": {
        "uz": "Tarifni tanlang:",
        "ru": "Выберите тариф:",
        "en": "Select a plan:"
    },
    "plan_free": {
        "uz": "Bepul",
        "ru": "Бесплатно",
        "en": "Free"
    },
    "plan_premium": {
        "uz": "Premium - {price} so'm",
        "ru": "Премиум - {price} сум",
        "en": "Premium - {price} UZS"
    },
    "not_enough_balance": {
        "uz": "Balans yetarli emas! Sizning balansingiz: {balance} so'm. Premium uchun {price} so'm kerak.",
        "ru": "Недостаточно средств! Ваш баланс: {balance} сум. Для премиума нужно {price} сум.",
        "en": "Insufficient balance! Your balance: {balance} UZS. Premium requires {price} UZS."
    },
    "enter_phone": {
        "uz": "Telefon raqamingizni yuboring:",
        "ru": "Отправьте ваш номер телефона:",
        "en": "Send your phone number:"
    },
    "btn_send_phone": {
        "uz": "Telefon raqamni yuborish",
        "ru": "Отправить номер телефона",
        "en": "Send phone number"
    },
    "enter_bot_name": {
        "uz": "Bot nomini kiriting (kamida 2 ta belgi):",
        "ru": "Введите название бота (минимум 2 символа):",
        "en": "Enter bot name (at least 2 characters):"
    },
    "bot_name_too_short": {
        "uz": "Bot nomi juda qisqa! Kamida 2 ta belgi bo'lishi kerak.",
        "ru": "Название слишком короткое! Минимум 2 символа.",
        "en": "Bot name is too short! At least 2 characters required."
    },
    "enter_bot_token": {
        "uz": "Bot tokenini kiriting:\n\n@BotFather dan olingan tokenni yuboring.\nMasalan: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        "ru": "Введите токен бота:\n\nОтправьте токен, полученный от @BotFather.\nНапример: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        "en": "Enter bot token:\n\nSend the token from @BotFather.\nExample: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    },
    "invalid_token_format": {
        "uz": "Token formati noto'g'ri! Token ':' belgisini o'z ichiga olishi kerak.",
        "ru": "Неверный формат токена! Токен должен содержать символ ':'.",
        "en": "Invalid token format! Token must contain ':' character."
    },
    "select_channel": {
        "uz": "Kanal tanlang:\n\nQuyidagi tugmani bosib, kanalni tanlang.",
        "ru": "Выберите канал:\n\nНажмите кнопку ниже и выберите канал.",
        "en": "Select channel:\n\nPress the button below and select a channel."
    },
    "btn_select_channel": {
        "uz": "Kanal tanlash",
        "ru": "Выбрать канал",
        "en": "Select channel"
    },
    "admin_warning": {
        "uz": "Botni kanalga admin qilib qo'shing!\n\nBot to'g'ri ishlashi uchun uni kanalga administrator sifatida qo'shishingiz shart.",
        "ru": "Добавьте бота администратором канала!\n\nДля корректной работы бот должен быть администратором канала.",
        "en": "Add bot as channel admin!\n\nThe bot must be added as administrator to the channel for proper operation."
    },
    "btn_understood": {
        "uz": "Tushundim",
        "ru": "Понял",
        "en": "Understood"
    },
    "enter_card_number": {
        "uz": "To'lov qabul qilish uchun karta raqamini kiriting (16 raqam):",
        "ru": "Введите номер карты для приёма платежей (16 цифр):",
        "en": "Enter card number to receive payments (16 digits):"
    },
    "invalid_card_number": {
        "uz": "Karta raqami noto'g'ri! 16 ta raqam kiriting.",
        "ru": "Неверный номер карты! Введите 16 цифр.",
        "en": "Invalid card number! Enter 16 digits."
    },
    "enter_monthly_price": {
        "uz": "Oylik obuna narxini kiriting (so'mda):",
        "ru": "Введите цену месячной подписки (в сумах):",
        "en": "Enter monthly subscription price (in UZS):"
    },
    "enter_yearly_price": {
        "uz": "Yillik obuna narxini kiriting (so'mda):",
        "ru": "Введите цену годовой подписки (в сумах):",
        "en": "Enter yearly subscription price (in UZS):"
    },
    "enter_unlimited_price": {
        "uz": "Cheksiz obuna narxini kiriting (so'mda):",
        "ru": "Введите цену безлимитной подписки (в сумах):",
        "en": "Enter unlimited subscription price (in UZS):"
    },
    "invalid_price": {
        "uz": "Narx noto'g'ri! Musbat son kiriting.",
        "ru": "Неверная цена! Введите положительное число.",
        "en": "Invalid price! Enter a positive number."
    },

    # ==================== BOT SUMMARY ====================
    "bot_summary": {
        "uz": "Bot ma'lumotlari:\n\n📛 Nomi: {name}\n📞 Telefon: {phone}\n💳 Karta: {card}\n📊 Narxlar:\n  • Oylik: {monthly} so'm\n  • Yillik: {yearly} so'm\n  • Cheksiz: {unlimited} so'm\n\nTasdiqlaysizmi?",
        "ru": "Данные бота:\n\n📛 Название: {name}\n📞 Телефон: {phone}\n💳 Карта: {card}\n📊 Цены:\n  • Месяц: {monthly} сум\n  • Год: {yearly} сум\n  • Безлимит: {unlimited} сум\n\nПодтверждаете?",
        "en": "Bot details:\n\n📛 Name: {name}\n📞 Phone: {phone}\n💳 Card: {card}\n📊 Prices:\n  • Monthly: {monthly} UZS\n  • Yearly: {yearly} UZS\n  • Unlimited: {unlimited} UZS\n\nConfirm?"
    },
    "btn_confirm": {
        "uz": "Tasdiqlash",
        "ru": "Подтвердить",
        "en": "Confirm"
    },
    "btn_cancel": {
        "uz": "Bekor qilish",
        "ru": "Отменить",
        "en": "Cancel"
    },
    "bot_created_success": {
        "uz": "Bot muvaffaqiyatli yaratildi!\n\nBot nomi: {name}\nBot username: @{username}\n\nBot ishga tushirildi.",
        "ru": "Бот успешно создан!\n\nНазвание бота: {name}\nUsername бота: @{username}\n\nБот запущен.",
        "en": "Bot created successfully!\n\nBot name: {name}\nBot username: @{username}\n\nBot is running."
    },
    "bot_creation_cancelled": {
        "uz": "Bot yaratish bekor qilindi.",
        "ru": "Создание бота отменено.",
        "en": "Bot creation cancelled."
    },

    # ==================== MY BOTS ====================
    "my_bots_title": {
        "uz": "Mening botlarim:",
        "ru": "Мои боты:",
        "en": "My bots:"
    },
    "no_bots": {
        "uz": "Sizda hali botlar yo'q.",
        "ru": "У вас пока нет ботов.",
        "en": "You don't have any bots yet."
    },
    "bot_status_active": {
        "uz": "Faol",
        "ru": "Активен",
        "en": "Active"
    },
    "bot_status_inactive": {
        "uz": "Nofaol",
        "ru": "Неактивен",
        "en": "Inactive"
    },

    # ==================== BALANCE ====================
    "your_balance": {
        "uz": "Sizning balansingiz: {balance} so'm",
        "ru": "Ваш баланс: {balance} сум",
        "en": "Your balance: {balance} UZS"
    },
    "btn_topup_balance": {
        "uz": "Balansni to'ldirish",
        "ru": "Пополнить баланс",
        "en": "Top up balance"
    },
    "enter_topup_amount": {
        "uz": "To'ldirish summasini kiriting (kamida 1,000 so'm):",
        "ru": "Введите сумму пополнения (минимум 1,000 сум):",
        "en": "Enter top-up amount (minimum 1,000 UZS):"
    },
    "min_topup_amount": {
        "uz": "Minimal summa 1,000 so'm",
        "ru": "Минимальная сумма 1,000 сум",
        "en": "Minimum amount is 1,000 UZS"
    },
    "topup_instructions": {
        "uz": "Quyidagi kartaga {amount} so'm o'tkazing:\n\n💳 {card}\n\nTo'lovni amalga oshirgach, skrinshot yuboring.",
        "ru": "Переведите {amount} сум на карту:\n\n💳 {card}\n\nПосле оплаты отправьте скриншот.",
        "en": "Transfer {amount} UZS to the card:\n\n💳 {card}\n\nAfter payment, send a screenshot."
    },
    "screenshot_received": {
        "uz": "Skrinshot qabul qilindi. Administrator tekshirgandan so'ng balansingiz to'ldiriladi.",
        "ru": "Скриншот получен. После проверки администратором ваш баланс будет пополнен.",
        "en": "Screenshot received. Your balance will be topped up after admin verification."
    },

    # ==================== ERRORS ====================
    "error_occurred": {
        "uz": "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        "ru": "Произошла ошибка. Попробуйте снова.",
        "en": "An error occurred. Please try again."
    },
    "no_permission": {
        "uz": "Ruxsat yo'q",
        "ru": "Нет доступа",
        "en": "No permission"
    },

    # ==================== BUTTONS ====================
    "btn_back": {
        "uz": "Orqaga",
        "ru": "Назад",
        "en": "Back"
    },
    "btn_main_menu": {
        "uz": "Asosiy menyu",
        "ru": "Главное меню",
        "en": "Main menu"
    },

    # ==================== HELP ====================
    "help_text": {
        "uz": "/start - Botni ishga tushirish\n/help - Yordam ko'rish\n/balance - Balansni ko'rish",
        "ru": "/start - Запустить бота\n/help - Помощь\n/balance - Проверить баланс",
        "en": "/start - Start bot\n/help - Help\n/balance - Check balance"
    },

    # ==================== MESSAGE HANDLER TRANSLATIONS ====================
    "contact_required": {
        "uz": "Iltimos, kontakt tugmasini bosing!",
        "ru": "Пожалуйста, нажмите кнопку контакта!",
        "en": "Please press the contact button!"
    },
    "invalid_phone": {
        "uz": "Noto'g'ri telefon raqami! Iltimos, qayta yo'llang.",
        "ru": "Неверный номер телефона! Попробуйте снова.",
        "en": "Invalid phone number! Please try again."
    },
    "msg_enter_bot_name": {
        "uz": "Bot nomini kiriting:\n\nMasalan: Birinchi Bot, kurs_bot, bot123",
        "ru": "Введите название бота:\n\nНапример: Первый Бот, kurs_bot, bot123",
        "en": "Enter bot name:\n\nExample: First Bot, kurs_bot, bot123"
    },
    "bot_name_short": {
        "uz": "Bot nomi juda qisqa! Iltimos, 2 harfdan uzun nom kiriting.",
        "ru": "Название слишком короткое! Введите минимум 2 символа.",
        "en": "Bot name is too short! Please enter at least 2 characters."
    },
    "msg_enter_token": {
        "uz": "Bot tokenini kiriting:\n\n1. @BotFather orqali /newbot komandasi yordamida bot yarating\n2. So'ngra BotFatherdan bot tokenini oling\n3. Quyidagi formatda tokenni kiriting:\n\nMisol: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ",
        "ru": "Введите токен бота:\n\n1. Создайте бота через @BotFather командой /newbot\n2. Получите токен от BotFather\n3. Введите токен в формате:\n\nПример: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ",
        "en": "Enter bot token:\n\n1. Create a bot via @BotFather with /newbot command\n2. Get the token from BotFather\n3. Enter the token in format:\n\nExample: 123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ"
    },
    "invalid_token": {
        "uz": "Noto'g'ri token!\n\n@BotFather dan olgan tokeningizni tekshiring va qayta jo'nating.",
        "ru": "Неверный токен!\n\nПроверьте токен от @BotFather и отправьте снова.",
        "en": "Invalid token!\n\nCheck your token from @BotFather and try again."
    },
    "select_channel_btn": {
        "uz": "Kanalimni tanlash",
        "ru": "Выбрать мой канал",
        "en": "Select my channel"
    },
    "msg_select_channel": {
        "uz": "Endi bot boshqarishi kerak bo'lgan kanalingizni tanlang:\n\nQuyidagi tugmani bosing va kanalingizni tanlang.",
        "ru": "Выберите канал, которым будет управлять бот:\n\nНажмите кнопку ниже и выберите канал.",
        "en": "Select the channel for the bot to manage:\n\nPress the button below and select your channel."
    },
    "channel_required": {
        "uz": "Iltimos, 'Kanalimni tanlash' tugmasini bosing va kanalingizni tanlang!",
        "ru": "Пожалуйста, нажмите 'Выбрать мой канал' и выберите канал!",
        "en": "Please press 'Select my channel' and choose your channel!"
    },
    "channel_accepted": {
        "uz": "Kanal qabul qilindi!\n\n<b>MUHIM OGOHLANTIRISH!</b>\n\nSiz @BotFather orqali yaratgan botingizni shu kanalga <b>ADMIN qilishingiz kerak</b>, aks holda bot to'g'ri ishlamaydi!\n\nIltimos hoziroq botingizni kanalingizga admin qiling va quyidagi tugmani bosing.",
        "ru": "Канал принят!\n\n<b>ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ!</b>\n\nВы должны добавить бота, созданного через @BotFather, <b>АДМИНИСТРАТОРОМ</b> в этот канал, иначе бот не будет работать!\n\nДобавьте бота администратором канала и нажмите кнопку ниже.",
        "en": "Channel accepted!\n\n<b>IMPORTANT WARNING!</b>\n\nYou must add the bot created via @BotFather as an <b>ADMIN</b> to this channel, otherwise the bot won't work!\n\nPlease add your bot as admin now and press the button below."
    },
    "understood_btn": {
        "uz": "Tushundim",
        "ru": "Понял",
        "en": "Understood"
    },
    "press_button": {
        "uz": "Iltimos, tugmani bosing!",
        "ru": "Пожалуйста, нажмите кнопку!",
        "en": "Please press the button!"
    },
    "invalid_card": {
        "uz": "Noto'g'ri karta raqami! 16 raqam bo'lishi kerak.",
        "ru": "Неверный номер карты! Должно быть 16 цифр.",
        "en": "Invalid card number! Must be 16 digits."
    },
    "prices_intro": {
        "uz": "Botingizda 3ta ta'rif mavjud.\n\nNarxlarni navbat bilan kiriting:\nOylik - (1 oy)\nYillik - (12 oy)\nCheksiz - (cheklanmagan muddat)\n\nOylik narxni kiriting (so'm, masalan: 50000):",
        "ru": "В вашем боте 3 тарифа.\n\nВведите цены по очереди:\nМесячный - (1 месяц)\nГодовой - (12 месяцев)\nБезлимит - (без ограничений)\n\nВведите месячную цену (сум, например: 50000):",
        "en": "Your bot has 3 pricing plans.\n\nEnter prices one by one:\nMonthly - (1 month)\nYearly - (12 months)\nUnlimited - (no time limit)\n\nEnter monthly price (UZS, e.g.: 50000):"
    },
    "msg_invalid_price": {
        "uz": "Noto'g'ri raqam! Iltimos, to'g'ri narxni kiriting.",
        "ru": "Неверное число! Введите корректную цену.",
        "en": "Invalid number! Please enter a valid price."
    },
    "enter_yearly": {
        "uz": "Yillik narxni kiriting (so'm, masalan: 500000):",
        "ru": "Введите годовую цену (сум, например: 500000):",
        "en": "Enter yearly price (UZS, e.g.: 500000):"
    },
    "enter_unlimited": {
        "uz": "Cheksiz (unlimited) narxni kiriting (so'm, masalan: 1000000):",
        "ru": "Введите безлимитную цену (сум, например: 1000000):",
        "en": "Enter unlimited price (UZS, e.g.: 1000000):"
    },
    "summary": {
        "uz": "<b>Qayta ko'rib chiqing</b>\n\nBot nomi: <b>{bot_name}</b>\nTarif: <b>{plan}</b>\nTel: <b>{phone}</b>\nKanal ID: <b>{channel}</b>\nKarta: <b>****{card}</b>\n\n<b>Narxlar:</b>\n  • Oylik: <b>{monthly:,.0f} so'm</b>\n  • Yillik: <b>{yearly:,.0f} so'm</b>\n  • Cheksiz: <b>{unlimited:,.0f} so'm</b>\n\nSiz quyidagi Tasdiqlash tugmasini bosish orqali <b>Terms of Service</b> shartlarni qabul qilasiz.",
        "ru": "<b>Проверьте данные</b>\n\nНазвание: <b>{bot_name}</b>\nТариф: <b>{plan}</b>\nТел: <b>{phone}</b>\nID канала: <b>{channel}</b>\nКарта: <b>****{card}</b>\n\n<b>Цены:</b>\n  • Месяц: <b>{monthly:,.0f} сум</b>\n  • Год: <b>{yearly:,.0f} сум</b>\n  • Безлимит: <b>{unlimited:,.0f} сум</b>\n\nНажав Подтвердить, вы принимаете <b>Условия использования</b>.",
        "en": "<b>Review details</b>\n\nBot name: <b>{bot_name}</b>\nPlan: <b>{plan}</b>\nPhone: <b>{phone}</b>\nChannel ID: <b>{channel}</b>\nCard: <b>****{card}</b>\n\n<b>Prices:</b>\n  • Monthly: <b>{monthly:,.0f} UZS</b>\n  • Yearly: <b>{yearly:,.0f} UZS</b>\n  • Unlimited: <b>{unlimited:,.0f} UZS</b>\n\nBy pressing Confirm, you accept the <b>Terms of Service</b>."
    },
    "confirm_btn": {
        "uz": "Tasdiqlash",
        "ru": "Подтвердить",
        "en": "Confirm"
    },
    "cancel_btn": {
        "uz": "Bekor qilish",
        "ru": "Отменить",
        "en": "Cancel"
    },

    # ==================== BALANCE HANDLER TRANSLATIONS ====================
    "not_registered": {
        "uz": "Siz hali ro'yxatdan o'tmagansiz.\n/start bosing.",
        "ru": "Вы еще не зарегистрированы.\nНажмите /start.",
        "en": "You are not registered yet.\nPress /start."
    },
    "balance_your_balance": {
        "uz": "<b>Sizning hisobingiz</b>\n\nJoriy balans: <b>{balance:,.0f} so'm</b>\n\nHisobni to'ldirish uchun quyidagi tugmani bosing:",
        "ru": "<b>Ваш счёт</b>\n\nТекущий баланс: <b>{balance:,.0f} сум</b>\n\nДля пополнения нажмите кнопку ниже:",
        "en": "<b>Your account</b>\n\nCurrent balance: <b>{balance:,.0f} UZS</b>\n\nPress the button below to top up:"
    },
    "btn_topup": {
        "uz": "Hisobni to'ldirish",
        "ru": "Пополнить счёт",
        "en": "Top up balance"
    },
    "topup_title": {
        "uz": "<b>Hisobni to'ldirish</b>\n\nQancha summa to'lamoqchisiz?\nSummani kiriting (faqat raqam, masalan: 50000):",
        "ru": "<b>Пополнение счёта</b>\n\nСколько хотите внести?\nВведите сумму (только число, например: 50000):",
        "en": "<b>Top up balance</b>\n\nHow much would you like to add?\nEnter amount (numbers only, e.g.: 50000):"
    },
    "min_amount": {
        "uz": "Minimal summa 1,000 so'm. Qayta kiriting:",
        "ru": "Минимальная сумма 1,000 сум. Введите заново:",
        "en": "Minimum amount is 1,000 UZS. Enter again:"
    },
    "invalid_amount": {
        "uz": "Faqat raqam kiriting (masalan: 50000):",
        "ru": "Введите только число (например: 50000):",
        "en": "Enter numbers only (e.g.: 50000):"
    },
    "payment_details": {
        "uz": "<b>To'lov ma'lumotlari</b>\n\nSumma: <b>{amount:,} so'm</b>\nKarta raqami: <code>{card}</code>\n\nYuqoridagi karta raqamiga <b>{amount:,} so'm</b> o'tkazing.\n\nTo'lovni amalga oshirgach, <b>screenshot</b> yuboring:",
        "ru": "<b>Данные для оплаты</b>\n\nСумма: <b>{amount:,} сум</b>\nНомер карты: <code>{card}</code>\n\nПереведите <b>{amount:,} сум</b> на указанную карту.\n\nПосле оплаты отправьте <b>скриншот</b>:",
        "en": "<b>Payment details</b>\n\nAmount: <b>{amount:,} UZS</b>\nCard number: <code>{card}</code>\n\nTransfer <b>{amount:,} UZS</b> to the card above.\n\nAfter payment, send a <b>screenshot</b>:"
    },
    "balance_screenshot_received": {
        "uz": "<b>Screenshot qabul qilindi!</b>\n\nAdmin tekshirib, tez orada tasdiqlaydi.\nSizga xabar yuboramiz.",
        "ru": "<b>Скриншот получен!</b>\n\nАдминистратор проверит и скоро подтвердит.\nМы вам сообщим.",
        "en": "<b>Screenshot received!</b>\n\nAdmin will verify and confirm soon.\nWe'll notify you."
    },
    "screenshot_error": {
        "uz": "Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.\nYoki admin bilan bog'laning.",
        "ru": "Произошла ошибка. Попробуйте позже.\nИли свяжитесь с администратором.",
        "en": "An error occurred. Please try again later.\nOr contact admin."
    },
    "send_screenshot": {
        "uz": "Iltimos, <b>screenshot (rasm)</b> yuboring.\nMatn emas, rasm kerak!",
        "ru": "Пожалуйста, отправьте <b>скриншот (изображение)</b>.\nНужно изображение, не текст!",
        "en": "Please send a <b>screenshot (image)</b>.\nAn image is needed, not text!"
    },
    "payment_confirmed": {
        "uz": "<b>To'lov tasdiqlandi!</b>\n\nQo'shilgan summa: <b>{amount:,} so'm</b>\nYangi balans: <b>{balance:,.0f} so'm</b>\n\nRahmat!",
        "ru": "<b>Оплата подтверждена!</b>\n\nДобавлено: <b>{amount:,} сум</b>\nНовый баланс: <b>{balance:,.0f} сум</b>\n\nСпасибо!",
        "en": "<b>Payment confirmed!</b>\n\nAdded: <b>{amount:,} UZS</b>\nNew balance: <b>{balance:,.0f} UZS</b>\n\nThank you!"
    },
    "payment_rejected": {
        "uz": "<b>To'lov rad etildi</b>\n\nSumma: <b>{amount:,} so'm</b>\n\nSabab: Screenshot noto'g'ri yoki to'lov amalga oshmagan.\nIltimos, qayta urinib ko'ring yoki admin bilan bog'laning.",
        "ru": "<b>Платёж отклонён</b>\n\nСумма: <b>{amount:,} сум</b>\n\nПричина: Неверный скриншот или оплата не поступила.\nПопробуйте снова или свяжитесь с администратором.",
        "en": "<b>Payment rejected</b>\n\nAmount: <b>{amount:,} UZS</b>\n\nReason: Invalid screenshot or payment not received.\nPlease try again or contact admin."
    },

    # ==================== CLIENT BOT ADMIN PANEL ====================
    "stats_title": {
        "uz": "<b>Batafsil Statistika</b>",
        "ru": "<b>Подробная статистика</b>",
        "en": "<b>Detailed Statistics</b>"
    },
    "bot_label": {
        "uz": "<b>Bot:</b>",
        "ru": "<b>Бот:</b>",
        "en": "<b>Bot:</b>"
    },
    "channel_label": {
        "uz": "<b>Kanal:</b>",
        "ru": "<b>Канал:</b>",
        "en": "<b>Channel:</b>"
    },
    "users_section": {
        "uz": "<b>Foydalanuvchilar:</b>",
        "ru": "<b>Пользователи:</b>",
        "en": "<b>Users:</b>"
    },
    "today_joined": {
        "uz": "Bugun qo'shilgan",
        "ru": "Сегодня присоединились",
        "en": "Joined today"
    },
    "total": {
        "uz": "Jami",
        "ru": "Всего",
        "en": "Total"
    },
    "active": {
        "uz": "Faol",
        "ru": "Активные",
        "en": "Active"
    },
    "removed": {
        "uz": "Chiqarilgan",
        "ru": "Удалённые",
        "en": "Removed"
    },
    "financial_section": {
        "uz": "<b>Moliyaviy:</b>",
        "ru": "<b>Финансы:</b>",
        "en": "<b>Financial:</b>"
    },
    "total_revenue": {
        "uz": "Umumiy daromad",
        "ru": "Общий доход",
        "en": "Total revenue"
    },
    "approved_amount": {
        "uz": "Tasdiqlangan",
        "ru": "Одобрено",
        "en": "Approved"
    },
    "rejected_amount": {
        "uz": "Bekor qilingan",
        "ru": "Отклонено",
        "en": "Rejected"
    },
    "pending_count": {
        "uz": "Kutilayotgan",
        "ru": "Ожидающие",
        "en": "Pending"
    },
    "subscription_section": {
        "uz": "<b>Obuna turlari (faol):</b>",
        "ru": "<b>Типы подписки (активные):</b>",
        "en": "<b>Subscription types (active):</b>"
    },
    "monthly_sub": {
        "uz": "1 oylik",
        "ru": "1 месяц",
        "en": "1 month"
    },
    "yearly_sub": {
        "uz": "1 yillik",
        "ru": "1 год",
        "en": "1 year"
    },
    "unlimited_sub": {
        "uz": "Cheksiz",
        "ru": "Безлимит",
        "en": "Unlimited"
    },
    "currency": {
        "uz": "so'm",
        "ru": "сум",
        "en": "UZS"
    },
    "people": {
        "uz": "kishi",
        "ru": "чел.",
        "en": "people"
    },
    "pcs": {
        "uz": "ta",
        "ru": "шт.",
        "en": "pcs"
    },
    "btn_stats": {
        "uz": "Statistika",
        "ru": "Статистика",
        "en": "Statistics"
    },
    "btn_users_excel": {
        "uz": "Userlar (Excel)",
        "ru": "Пользователи (Excel)",
        "en": "Users (Excel)"
    },
    "btn_payments_excel": {
        "uz": "To'lovlar (Excel)",
        "ru": "Платежи (Excel)",
        "en": "Payments (Excel)"
    },
    "btn_active_users": {
        "uz": "Aktiv userlar",
        "ru": "Активные",
        "en": "Active users"
    },
    "btn_removed_users": {
        "uz": "Chiqarilganlar",
        "ru": "Удалённые",
        "en": "Removed"
    },
    "users_preparing": {
        "uz": "Userlar ro'yxati tayyorlanmoqda...",
        "ru": "Подготовка списка пользователей...",
        "en": "Preparing users list..."
    },
    "payments_preparing": {
        "uz": "To'lovlar ro'yxati tayyorlanmoqda...",
        "ru": "Подготовка списка платежей...",
        "en": "Preparing payments list..."
    },
    "users_list_title": {
        "uz": "<b>Userlar ro'yxati</b>",
        "ru": "<b>Список пользователей</b>",
        "en": "<b>Users list</b>"
    },
    "payments_list_title": {
        "uz": "<b>To'lovlar ro'yxati</b>",
        "ru": "<b>Список платежей</b>",
        "en": "<b>Payments list</b>"
    },
    "total_users": {
        "uz": "Jami",
        "ru": "Всего",
        "en": "Total"
    },
    "total_payments": {
        "uz": "Jami",
        "ru": "Всего",
        "en": "Total"
    },
    "excel_error": {
        "uz": "Excel yaratishda xatolik yuz berdi",
        "ru": "Ошибка при создании Excel",
        "en": "Error creating Excel file"
    },
    "excel_num": {
        "uz": "#",
        "ru": "#",
        "en": "#"
    },
    "excel_user_id": {
        "uz": "User ID",
        "ru": "User ID",
        "en": "User ID"
    },
    "excel_username": {
        "uz": "Username",
        "ru": "Username",
        "en": "Username"
    },
    "excel_name": {
        "uz": "Ism",
        "ru": "Имя",
        "en": "Name"
    },
    "excel_duration": {
        "uz": "Muddat",
        "ru": "Срок",
        "en": "Duration"
    },
    "excel_status": {
        "uz": "Status",
        "ru": "Статус",
        "en": "Status"
    },
    "excel_balance": {
        "uz": "Balans",
        "ru": "Баланс",
        "en": "Balance"
    },
    "excel_date": {
        "uz": "Qo'shilgan sana",
        "ru": "Дата добавления",
        "en": "Join date"
    },
    "excel_trans_id": {
        "uz": "ID",
        "ru": "ID",
        "en": "ID"
    },
    "excel_amount": {
        "uz": "Summa",
        "ru": "Сумма",
        "en": "Amount"
    },
    "excel_type": {
        "uz": "Turi",
        "ru": "Тип",
        "en": "Type"
    },
    "excel_trans_date": {
        "uz": "Sana",
        "ru": "Дата",
        "en": "Date"
    },
    "trans_plan_purchase": {
        "uz": "Tarif sotib olish",
        "ru": "Покупка тарифа",
        "en": "Plan purchase"
    },
    "trans_topup": {
        "uz": "Hisobni to'ldirish",
        "ru": "Пополнение счёта",
        "en": "Balance top-up"
    },
    "status_approved": {
        "uz": "Tasdiqlangan",
        "ru": "Одобрено",
        "en": "Approved"
    },
    "status_rejected": {
        "uz": "Bekor qilingan",
        "ru": "Отклонено",
        "en": "Rejected"
    },
    "status_pending": {
        "uz": "Kutilmoqda",
        "ru": "Ожидает",
        "en": "Pending"
    },
    "active_users_title": {
        "uz": "<b>Aktiv userlar</b>",
        "ru": "<b>Активные пользователи</b>",
        "en": "<b>Active users</b>"
    },
    "removed_users_title": {
        "uz": "<b>Chiqarilgan userlar</b>",
        "ru": "<b>Удалённые пользователи</b>",
        "en": "<b>Removed users</b>"
    },
    "no_active_users": {
        "uz": "<i>Hozircha aktiv userlar yo'q.</i>",
        "ru": "<i>Пока нет активных пользователей.</i>",
        "en": "<i>No active users yet.</i>"
    },
    "no_removed_users": {
        "uz": "<i>Hozircha chiqarilgan userlar yo'q.</i>",
        "ru": "<i>Пока нет удалённых пользователей.</i>",
        "en": "<i>No removed users yet.</i>"
    },
    "duration_label": {
        "uz": "Muddat",
        "ru": "Срок",
        "en": "Duration"
    },
    "last_10_shown": {
        "uz": "<i>Oxirgi 10ta ko'rsatildi. Jami: {total} ta</i>",
        "ru": "<i>Показаны последние 10. Всего: {total}</i>",
        "en": "<i>Last 10 shown. Total: {total}</i>"
    },
    "admin_panel_title": {
        "uz": "<b>Admin Panel</b>",
        "ru": "<b>Панель администратора</b>",
        "en": "<b>Admin Panel</b>"
    },
    "channel_id_label": {
        "uz": "<b>Kanal ID:</b>",
        "ru": "<b>ID канала:</b>",
        "en": "<b>Channel ID:</b>"
    },
    "short_stats": {
        "uz": "<b>Qisqacha statistika:</b>",
        "ru": "<b>Краткая статистика:</b>",
        "en": "<b>Brief statistics:</b>"
    },
    "total_users_label": {
        "uz": "Jami userlar",
        "ru": "Всего пользователей",
        "en": "Total users"
    },
    "active_label": {
        "uz": "Faol",
        "ru": "Активные",
        "en": "Active"
    },
    "removed_label": {
        "uz": "Chiqarilgan",
        "ru": "Удалённые",
        "en": "Removed"
    },
    "revenue_label": {
        "uz": "Daromad",
        "ru": "Доход",
        "en": "Revenue"
    },

    # ==================== CLIENT BOT WELCOME ====================
    "cb_greeting": {
        "uz": "Assalomu alaykum, {name}!",
        "ru": "Привет, {name}!",
        "en": "Hello, {name}!"
    },
    "cb_welcome": {
        "uz": "<b>{bot_name}</b> botiga xush kelibsiz!",
        "ru": "Добро пожаловать в бот <b>{bot_name}</b>!",
        "en": "Welcome to <b>{bot_name}</b> bot!"
    },
    "cb_select_duration": {
        "uz": "<b>Telegram kanalga a'zo bo'lish uchun muddatni tanlang:</b>",
        "ru": "<b>Выберите продолжительность подписки на канал:</b>",
        "en": "<b>Select subscription duration for the channel:</b>"
    },
    "cb_test": {
        "uz": "Test - 2 daqiqa (Bepul)",
        "ru": "Тест - 2 минуты (Бесплатно)",
        "en": "Test - 2 minutes (Free)"
    },
    "cb_monthly": {
        "uz": "Oylik",
        "ru": "Месячная",
        "en": "Monthly"
    },
    "cb_yearly": {
        "uz": "Yillik",
        "ru": "Годовая",
        "en": "Yearly"
    },
    "cb_unlimited": {
        "uz": "Cheksiz",
        "ru": "Неограниченная",
        "en": "Unlimited"
    },
    "cb_topup": {
        "uz": "Hisobni to'ldirish",
        "ru": "Пополнить баланс",
        "en": "Top up balance"
    },

    # ==================== BOT EDIT ====================
    "edit_select_field": {
        "uz": "✏️ <b>Tahrirlash</b>\n\nNimani o'zgartirmoqchisiz?",
        "ru": "✏️ <b>Редактирование</b>\n\nЧто хотите изменить?",
        "en": "✏️ <b>Edit</b>\n\nWhat would you like to change?"
    },
    "edit_card_btn": {
        "uz": "💳 Karta raqami",
        "ru": "💳 Номер карты",
        "en": "💳 Card number"
    },
    "edit_prices_btn": {
        "uz": "💰 Narxlar",
        "ru": "💰 Цены",
        "en": "💰 Prices"
    },
    "edit_bot_stopping": {
        "uz": "⏳ Bot to'xtatilmoqda...\n\nO'zgarishlar kiritish uchun bot vaqtincha to'xtatiladi.",
        "ru": "⏳ Бот останавливается...\n\nДля внесения изменений бот временно остановлен.",
        "en": "⏳ Bot is stopping...\n\nBot is temporarily stopped for editing."
    },
    "edit_bot_stopped": {
        "uz": "✅ Bot to'xtatildi.\n\nEndi o'zgarishlar kiritishingiz mumkin.",
        "ru": "✅ Бот остановлен.\n\nТеперь можете вносить изменения.",
        "en": "✅ Bot stopped.\n\nYou can now make changes."
    },
    "edit_enter_card": {
        "uz": "💳 Yangi karta raqamini kiriting (16 raqam):\n\nJoriy karta: {current_card}",
        "ru": "💳 Введите новый номер карты (16 цифр):\n\nТекущая карта: {current_card}",
        "en": "💳 Enter new card number (16 digits):\n\nCurrent card: {current_card}"
    },
    "edit_enter_oy_narx": {
        "uz": "💰 Yangi oylik narxni kiriting (so'm):\n\nJoriy narx: {current_price} so'm",
        "ru": "💰 Введите новую месячную цену (сум):\n\nТекущая цена: {current_price} сум",
        "en": "💰 Enter new monthly price (UZS):\n\nCurrent price: {current_price} UZS"
    },
    "edit_enter_yil_narx": {
        "uz": "💰 Yangi yillik narxni kiriting (so'm):\n\nJoriy narx: {current_price} so'm",
        "ru": "💰 Введите новую годовую цену (сум):\n\nТекущая цена: {current_price} сум",
        "en": "💰 Enter new yearly price (UZS):\n\nCurrent price: {current_price} UZS"
    },
    "edit_enter_cheksiz_narx": {
        "uz": "💰 Yangi cheksiz narxni kiriting (so'm):\n\nJoriy narx: {current_price} so'm",
        "ru": "💰 Введите новую безлимитную цену (сум):\n\nТекущая цена: {current_price} сум",
        "en": "💰 Enter new unlimited price (UZS):\n\nCurrent price: {current_price} UZS"
    },
    "edit_card_saved": {
        "uz": "✅ Karta raqami saqlandi!\n\nYangi karta: {new_card}",
        "ru": "✅ Номер карты сохранён!\n\nНовая карта: {new_card}",
        "en": "✅ Card number saved!\n\nNew card: {new_card}"
    },
    "edit_prices_saved": {
        "uz": "✅ Narxlar saqlandi!\n\n💰 Oylik: {oy_narx} so'm\n💰 Yillik: {yil_narx} so'm\n💰 Cheksiz: {cheksiz_narx} so'm",
        "ru": "✅ Цены сохранены!\n\n💰 Месяц: {oy_narx} сум\n💰 Год: {yil_narx} сум\n💰 Безлимит: {cheksiz_narx} сум",
        "en": "✅ Prices saved!\n\n💰 Monthly: {oy_narx} UZS\n💰 Yearly: {yil_narx} UZS\n💰 Unlimited: {cheksiz_narx} UZS"
    },
    "edit_confirm_restart": {
        "uz": "🔄 Botni qayta ishga tushirish uchun <b>Tasdiqlash</b> tugmasini bosing.",
        "ru": "🔄 Нажмите <b>Подтвердить</b> для перезапуска бота.",
        "en": "🔄 Press <b>Confirm</b> to restart the bot."
    },
    "edit_bot_restarting": {
        "uz": "⏳ Bot qayta ishga tushirilmoqda...",
        "ru": "⏳ Бот перезапускается...",
        "en": "⏳ Bot is restarting..."
    },
    "edit_bot_restarted": {
        "uz": "✅ Bot muvaffaqiyatli qayta ishga tushirildi!",
        "ru": "✅ Бот успешно перезапущен!",
        "en": "✅ Bot restarted successfully!"
    },
    "edit_cancelled": {
        "uz": "❌ Tahrirlash bekor qilindi.",
        "ru": "❌ Редактирование отменено.",
        "en": "❌ Edit cancelled."
    },
    "edit_skip_btn": {
        "uz": "⏭ O'tkazib yuborish",
        "ru": "⏭ Пропустить",
        "en": "⏭ Skip"
    },
    "edit_continue_btn": {
        "uz": "➡️ Davom etish",
        "ru": "➡️ Продолжить",
        "en": "➡️ Continue"
    },
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """
    Get translated text by key and language.

    Args:
        key: Translation key
        lang: Language code (uz, ru, en)
        **kwargs: Format parameters for the text

    Returns:
        Translated text or key if not found
    """
    if key not in TRANSLATIONS:
        return key

    translation = TRANSLATIONS[key]

    # Default to Uzbek if language not found
    if lang not in translation:
        lang = "uz"

    text = translation.get(lang, translation.get("uz", key))

    # Format text with provided kwargs
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


def get_language_keyboard():
    """
    Returns language selection keyboard buttons data.
    """
    return [
        {"text": "O'zbekcha", "callback_data": "set_lang_uz"},
        {"text": "Русский", "callback_data": "set_lang_ru"},
        {"text": "English", "callback_data": "set_lang_en"}
    ]


# Shortcut function
_ = get_text
