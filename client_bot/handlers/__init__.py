"""
Client Bot Handlers Package
"""
from client_bot.handlers.start import register_start_handlers
from client_bot.handlers.balance import register_balance_handlers
from client_bot.handlers.plans import register_plan_handlers
from client_bot.handlers.admin import register_admin_handlers


def register_all_handlers(dp, bot, owner_id: int, bot_name: str, bot_token: str, bot_db_id: int):
    """Register all handlers to dispatcher"""
    register_start_handlers(dp, bot, owner_id, bot_name, bot_token, bot_db_id)
    register_balance_handlers(dp, bot, owner_id, bot_token, bot_db_id)
    register_plan_handlers(dp, bot, owner_id, bot_token, bot_db_id)
    register_admin_handlers(dp, bot, owner_id, bot_token, bot_db_id)


__all__ = ["register_all_handlers"]
