"""
FSM States for Client Bot
"""
from aiogram.fsm.state import State, StatesGroup


class LanguageStates(StatesGroup):
    """States for language selection"""
    selecting_language = State()


class BalanceStates(StatesGroup):
    """States for balance top-up flow"""
    waiting_for_amount = State()
    waiting_for_screenshot = State()
