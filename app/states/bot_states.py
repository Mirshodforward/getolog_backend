from aiogram.fsm.state import State, StatesGroup


class BotCreationStates(StatesGroup):
    """Bot creation states"""
    selecting_plan = State()
    confirming_plan = State()
    # Client registration
    entering_phone = State()
    # Bot info
    entering_bot_token = State()
    entering_channel_link = State()
    admin_warning = State()
    entering_card_number = State()
    entering_oy_narx = State()
    entering_yil_narx = State()
    entering_cheksiz_narx = State()
    confirming_terms = State()


class BotEditStates(StatesGroup):
    """Bot tahrirlash uchun state-lar"""
    selecting_field = State()  # Nimani tahrirlash: karta yoki narxlar
    editing_card = State()  # Karta raqamini kiritish
    editing_oy_narx = State()  # Oylik narxni kiritish
    editing_yil_narx = State()  # Yillik narxni kiritish
    editing_cheksiz_narx = State()  # Cheksiz narxni kiritish
    confirming_changes = State()  # O'zgarishlarni tasdiqlash


class BroadcastStates(StatesGroup):
    """Broadcast xabar yuborish uchun state-lar"""
    selecting_audience = State()  # Auditoriya tanlash: clients, users, all
    entering_message = State()  # Xabar matnini kiritish
    confirming_broadcast = State()  # Tasdiqlash
