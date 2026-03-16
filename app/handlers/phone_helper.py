from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.states import BotCreationStates

def get_enter_token_msg(lang: str) -> str:
    msgs = {
        "uz": "🔑 <b>Bot tokenini kiriting:</b>\n\n1. @BotFather orqali /newbot komandasi yordamida bot yarating\n2. So'ngra BotFatherdan bot tokenini oling\n3. Quyidagi formatda tokenni kiriting:\n\nMisol: <code>123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ</code>",
        "ru": "🔑 <b>Введите токен бота:</b>\n\n1. Создайте бота через @BotFather командой /newbot\n2. Получите токен от BotFather\n3. Введите токен в формате:\n\nПример: <code>123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ</code>",
        "en": "🔑 <b>Enter bot token:</b>\n\n1. Create a bot via @BotFather with /newbot command\n2. Get the token from BotFather\n3. Enter the token in format:\n\nExample: <code>123456789:AABCdefGhIJKlmNoPQRsTUVwxyZ</code>"
    }
    return msgs.get(lang, msgs["uz"])

async def ask_for_phone_or_token(callback: CallbackQuery, state: FSMContext, lang: str, client, prefix_msg_dict: dict = None):
    prefix = prefix_msg_dict.get(lang, "") if prefix_msg_dict else ""
    
    if client and client.phone_number:
        # User already has a phone number saved
        await state.update_data(phone=client.phone_number)
        
        msg = f"{prefix}\n\n{get_enter_token_msg(lang)}"
        
        await callback.message.edit_text(msg.strip(), parse_mode="HTML")
        await state.set_state(BotCreationStates.entering_bot_token)
    else:
        # Needs to share contact
        btn_text = {"uz": "📱 Kontaktni ulashish", "ru": "📱 Поделиться контактом", "en": "📱 Share contact"}
        msg1 = {"uz": "📞 Iltimos, kontaktingizni ulashish tugmasini bosing:", "ru": "📞 Пожалуйста, нажмите кнопку для отправки контакта:", "en": "📞 Please press the button to share your contact:"}
        msg2 = {"uz": "👇 Quyidagi tugmani bosing:", "ru": "👇 Нажмите кнопку ниже:", "en": "👇 Press the button below:"}

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=btn_text.get(lang, btn_text["uz"]), request_contact=True)],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        edit_text = f"{prefix}\n\n{msg1.get(lang, msg1['uz'])}" if prefix else msg1.get(lang, msg1['uz'])
        await callback.message.edit_text(edit_text.strip(), parse_mode="HTML")
        await callback.message.answer(msg2.get(lang, msg2["uz"]), reply_markup=keyboard)
        await state.set_state(BotCreationStates.entering_phone)

    await callback.answer()
