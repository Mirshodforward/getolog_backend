"""
Message Handlers Package

Aiogram routers for handling:
- start_router: /start command and main menu
- callback_router: Inline button callbacks
- message_router: Text message handling
- balance_router: Balance and payment operations
"""
from app.handlers.start_handler import router as start_router
from app.handlers.callback_handler import router as callback_router
from app.handlers.message_handler import router as message_router
from app.handlers.balance_handler import router as balance_router
from app.handlers.renew_plan_handler import router as renew_plan_router

__all__ = ["start_router", "callback_router", "message_router", "balance_router", "renew_plan_router"]
