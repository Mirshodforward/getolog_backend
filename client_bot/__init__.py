"""
Client Bot Package - Individual user bots

This package contains the client bot that runs as a separate process
for each bot created by clients. Each bot handles:
- User subscription management
- Payment processing
- Channel access control
- Admin panel for bot owner

Modules:
- main: Bot entry point and initialization
- config: Bot configuration and logging
- states: FSM states for conversation flow
- handlers: Message and callback handlers
- utils: Database and scheduler utilities
"""
from client_bot.main import start_client_bot

__all__ = ["start_client_bot"]
