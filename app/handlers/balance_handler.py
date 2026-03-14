from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import BalanceStates
from app.database import AsyncSessionLocal
from app.crud import get_client_by_user_id, update_client_balance, create_transaction, update_transaction_status
from app.config import settings

router = Router()


# Translation dictionaries
BALANCE_MSGS = {
    "not_registered": {
        "uz": "❌ Siz hali ro'yxatdan o'tmagansiz.\n/start bosing.",
        "ru": "❌ Вы еще не зарегистрированы.\nНажмите /start.",
        "en": "❌ You are not registered yet.\nPress /start."
    },
    "your_balance": {
        "uz": "💰 <b>Sizning hisobingiz</b>\n\n📊 Joriy balans: <b>{balance:,.0f} so'm</b>\n\nHisobni to'ldirish uchun quyidagi tugmani bosing:",
        "ru": "💰 <b>Ваш счёт</b>\n\n📊 Текущий баланс: <b>{balance:,.0f} сум</b>\n\nДля пополнения нажмите кнопку ниже:",
        "en": "💰 <b>Your account</b>\n\n📊 Current balance: <b>{balance:,.0f} UZS</b>\n\nPress the button below to top up:"
    },
    "btn_topup": {
        "uz": "💳 Hisobni to'ldirish",
        "ru": "💳 Пополнить счёт",
        "en": "💳 Top up balance"
    },
    "topup_title": {
        "uz": "💳 <b>Hisobni to'ldirish</b>\n\nQancha summa to'lamoqchisiz?\nSummani kiriting (faqat raqam, masalan: 50000):",
        "ru": "💳 <b>Пополнение счёта</b>\n\nСколько хотите внести?\nВведите сумму (только число, например: 50000):",
        "en": "💳 <b>Top up balance</b>\n\nHow much would you like to add?\nEnter amount (numbers only, e.g.: 50000):"
    },
    "min_amount": {
        "uz": "❌ Minimal summa 1,000 so'm. Qayta kiriting:",
        "ru": "❌ Минимальная сумма 1,000 сум. Введите заново:",
        "en": "❌ Minimum amount is 1,000 UZS. Enter again:"
    },
    "invalid_amount": {
        "uz": "❌ Faqat raqam kiriting (masalan: 50000):",
        "ru": "❌ Введите только число (например: 50000):",
        "en": "❌ Enter numbers only (e.g.: 50000):"
    },
    "payment_details": {
        "uz": "💳 <b>To'lov ma'lumotlari</b>\n\n📍 Summa: <b>{amount:,} so'm</b>\n💳 Karta raqami: <code>{card}</code>\n\n☝️ Yuqoridagi karta raqamiga <b>{amount:,} so'm</b> o'tkazing.\n\n✅ To'lovni amalga oshirgach, <b>screenshot</b> yuboring:",
        "ru": "💳 <b>Данные для оплаты</b>\n\n📍 Сумма: <b>{amount:,} сум</b>\n💳 Номер карты: <code>{card}</code>\n\n☝️ Переведите <b>{amount:,} сум</b> на указанную карту.\n\n✅ После оплаты отправьте <b>скриншот</b>:",
        "en": "💳 <b>Payment details</b>\n\n📍 Amount: <b>{amount:,} UZS</b>\n💳 Card number: <code>{card}</code>\n\n☝️ Transfer <b>{amount:,} UZS</b> to the card above.\n\n✅ After payment, send a <b>screenshot</b>:"
    },
    "screenshot_received": {
        "uz": "✅ <b>Screenshot qabul qilindi!</b>\n\n⏳ Admin tekshirib, tez orada tasdiqlaydi.\nSizga xabar yuboramiz.",
        "ru": "✅ <b>Скриншот получен!</b>\n\n⏳ Администратор проверит и скоро подтвердит.\nМы вам сообщим.",
        "en": "✅ <b>Screenshot received!</b>\n\n⏳ Admin will verify and confirm soon.\nWe'll notify you."
    },
    "screenshot_error": {
        "uz": "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.\nYoki admin bilan bog'laning.",
        "ru": "❌ Произошла ошибка. Попробуйте позже.\nИли свяжитесь с администратором.",
        "en": "❌ An error occurred. Please try again later.\nOr contact admin."
    },
    "send_screenshot": {
        "uz": "❌ Iltimos, <b>screenshot (rasm)</b> yuboring.\nMatn emas, rasm kerak!",
        "ru": "❌ Пожалуйста, отправьте <b>скриншот (изображение)</b>.\nНужно изображение, не текст!",
        "en": "❌ Please send a <b>screenshot (image)</b>.\nAn image is needed, not text!"
    },
    "payment_confirmed": {
        "uz": "✅ <b>To'lov tasdiqlandi!</b>\n\n💰 Qo'shilgan summa: <b>{amount:,} so'm</b>\n📊 Yangi balans: <b>{balance:,.0f} so'm</b>\n\nRahmat! 🎉",
        "ru": "✅ <b>Оплата подтверждена!</b>\n\n💰 Добавлено: <b>{amount:,} сум</b>\n📊 Новый баланс: <b>{balance:,.0f} сум</b>\n\nСпасибо! 🎉",
        "en": "✅ <b>Payment confirmed!</b>\n\n💰 Added: <b>{amount:,} UZS</b>\n📊 New balance: <b>{balance:,.0f} UZS</b>\n\nThank you! 🎉"
    },
    "payment_rejected": {
        "uz": "❌ <b>To'lov rad etildi</b>\n\n💰 Summa: <b>{amount:,} so'm</b>\n\nSabab: Screenshot noto'g'ri yoki to'lov amalga oshmagan.\nIltimos, qayta urinib ko'ring yoki admin bilan bog'laning.",
        "ru": "❌ <b>Платёж отклонён</b>\n\n💰 Сумма: <b>{amount:,} сум</b>\n\nПричина: Неверный скриншот или оплата не поступила.\nПопробуйте снова или свяжитесь с администратором.",
        "en": "❌ <b>Payment rejected</b>\n\n💰 Amount: <b>{amount:,} UZS</b>\n\nReason: Invalid screenshot or payment not received.\nPlease try again or contact admin."
    }
}


def get_balance_msg(key: str, lang: str = "uz", **kwargs) -> str:
    """Get balance message by key and language"""
    if key in BALANCE_MSGS:
        text = BALANCE_MSGS[key].get(lang, BALANCE_MSGS[key].get("uz", key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    return key


@router.message(Command("balance"))
async def balance_command(message: Message, state: FSMContext) -> None:
    """Balance command - show current balance and top-up option"""
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)

    if not client:
        await message.answer(get_balance_msg("not_registered", "uz"))
        return

    lang = client.language or "uz"
    current_balance = float(client.balance) if client.balance else 0

    # Save language to state
    await state.update_data(lang=lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_balance_msg("btn_topup", lang), callback_data="topup_balance")],
    ])

    await message.answer(
        get_balance_msg("your_balance", lang, balance=current_balance),
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "topup_balance")
async def topup_balance_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Start top-up process"""
    user_id = callback.from_user.id

    # Get language
    async with AsyncSessionLocal() as session:
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

    await state.update_data(lang=lang)

    await callback.message.edit_text(
        get_balance_msg("topup_title", lang),
        parse_mode="HTML"
    )
    await state.set_state(BalanceStates.entering_amount)
    await callback.answer()


@router.message(BalanceStates.entering_amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    """Process entered amount"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount < 1000:
            await message.answer(get_balance_msg("min_amount", lang))
            return
    except ValueError:
        await message.answer(get_balance_msg("invalid_amount", lang))
        return

    await state.update_data(amount=amount)

    await message.answer(
        get_balance_msg("payment_details", lang, amount=amount, card=settings.CARD_NUMBER),
        parse_mode="HTML"
    )
    await state.set_state(BalanceStates.waiting_screenshot)


@router.message(BalanceStates.waiting_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process screenshot and send to admin"""
    user_id = message.from_user.id
    username = message.from_user.username or "Noma'lum"
    full_name = message.from_user.full_name or "Noma'lum"

    data = await state.get_data()
    amount = data.get("amount", 0)
    lang = data.get("lang", "uz")

    # Get the largest photo
    photo = message.photo[-1]

    # Create transaction record
    async with AsyncSessionLocal() as session:
        transaction = await create_transaction(
            session=session,
            user_id=user_id,
            username=username,
            amount=amount,
            role="client_topup",
            status="pending"
        )
        transaction_id = transaction.id

    # Create keyboard for admin with transaction ID
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_payment_{transaction_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"reject_payment_{transaction_id}"),
        ],
    ])

    # Send to admin
    try:
        await bot.send_photo(
            chat_id=settings.ADMIN_ID,
            photo=photo.file_id,
            caption=(
                f"💳 <b>Yangi to'lov so'rovi</b>\n\n"
                f"👤 Foydalanuvchi: {full_name}\n"
                f"🆔 Username: @{username}\n"
                f"🔢 User ID: <code>{user_id}</code>\n"
                f"💰 Summa: <b>{amount:,} so'm</b>\n"
                f"🆔 Transaction ID: <code>{transaction_id}</code>\n\n"
                f"Tasdiqlaysizmi?"
            ),
            reply_markup=admin_keyboard,
            parse_mode="HTML"
        )

        await message.answer(
            get_balance_msg("screenshot_received", lang),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(get_balance_msg("screenshot_error", lang))

    await state.clear()


@router.message(BalanceStates.waiting_screenshot)
async def waiting_screenshot_invalid(message: Message, state: FSMContext) -> None:
    """Handle non-photo messages while waiting for screenshot"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await message.answer(
        get_balance_msg("send_screenshot", lang),
        parse_mode="HTML"
    )


# Admin confirmation handlers
@router.callback_query(F.data.startswith("confirm_payment_"))
async def admin_confirm_payment(callback: CallbackQuery, bot: Bot) -> None:
    """Admin confirms payment"""
    # Check if admin
    if callback.from_user.id != settings.ADMIN_ID:
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    # Parse data: confirm_payment_{transaction_id}
    parts = callback.data.split("_")
    transaction_id = int(parts[2])
    admin_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        # Get transaction
        from app.crud import get_transaction_by_id
        transaction = await get_transaction_by_id(session, transaction_id)

        if not transaction:
            await callback.answer("❌ Transaction topilmadi!", show_alert=True)
            return

        user_id = transaction.user_id
        amount = float(transaction.amount)

        # Update transaction status
        await update_transaction_status(session, transaction_id, "approved", admin_id)

        # Update client balance
        client = await update_client_balance(session, user_id, amount)

    if client:
        new_balance = float(client.balance) if client.balance else 0
        lang = client.language or "uz"

        # Notify user
        try:
            await bot.send_message(
                chat_id=user_id,
                text=get_balance_msg("payment_confirmed", lang, amount=amount, balance=new_balance),
                parse_mode="HTML"
            )
        except Exception:
            pass

        # Update admin message
        await callback.message.edit_caption(
            caption=(
                f"{callback.message.caption}\n\n"
                f"✅ <b>TASDIQLANGAN</b>\n"
                f"Admin: {callback.from_user.full_name}"
            ),
            parse_mode="HTML"
        )
        await callback.answer("✅ To'lov tasdiqlandi!", show_alert=True)
    else:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)


@router.callback_query(F.data.startswith("reject_payment_"))
async def admin_reject_payment(callback: CallbackQuery, bot: Bot) -> None:
    """Admin rejects payment"""
    # Check if admin
    if callback.from_user.id != settings.ADMIN_ID:
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    # Parse data: reject_payment_{transaction_id}
    parts = callback.data.split("_")
    transaction_id = int(parts[2])
    admin_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        # Get transaction
        from app.crud import get_transaction_by_id
        transaction = await get_transaction_by_id(session, transaction_id)

        if not transaction:
            await callback.answer("❌ Transaction topilmadi!", show_alert=True)
            return

        user_id = transaction.user_id
        amount = float(transaction.amount)

        # Update transaction status
        await update_transaction_status(session, transaction_id, "rejected", admin_id)

        # Get client language
        client = await get_client_by_user_id(session, user_id)
        lang = client.language if client else "uz"

    # Notify user
    try:
        await bot.send_message(
            chat_id=user_id,
            text=get_balance_msg("payment_rejected", lang, amount=amount),
            parse_mode="HTML"
        )
    except Exception:
        pass

    # Update admin message
    await callback.message.edit_caption(
        caption=(
            f"{callback.message.caption}\n\n"
            f"❌ <b>RAD ETILGAN</b>\n"
            f"Admin: {callback.from_user.full_name}"
        ),
        parse_mode="HTML"
    )
    await callback.answer("❌ To'lov rad etildi!", show_alert=True)
