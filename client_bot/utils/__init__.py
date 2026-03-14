"""
Client Bot Utils Package

Provides utility functions for:
- Database operations (user management, bot info)
- Scheduler for auto-kick feature
"""
from client_bot.utils.database import (
    get_or_create_user,
    get_bot_info,
    get_client_plan,
    get_client_language
)
from client_bot.utils.scheduler import (
    kick_user_from_channel,
    schedule_kick,
    scheduler
)

__all__ = [
    "get_or_create_user",
    "get_bot_info",
    "get_client_plan",
    "get_client_language",
    "kick_user_from_channel",
    "schedule_kick",
    "scheduler"
]
