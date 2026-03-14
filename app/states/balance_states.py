from aiogram.fsm.state import State, StatesGroup


class BalanceStates(StatesGroup):
    """Balance top-up states"""
    entering_amount = State()      # Summa kiritish
    waiting_screenshot = State()   # Screenshot kutish
    waiting_admin = State()        # Admin tasdiqlashini kutish
