from aiogram.fsm.state import State, StatesGroup


class ClientStates(StatesGroup):
    """Client registration states"""
    enter_phone = State()
    enter_username = State()
    confirm_registration = State()
