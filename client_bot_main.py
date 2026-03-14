"""
Client Bot Entry Point - Wrapper for the modular client_bot package

This file is kept for backward compatibility with the existing bot launch system.
The actual bot code is organized in the client_bot/ package.

Structure:
    client_bot/
    ├── __init__.py
    ├── config.py           # Configuration and logging
    ├── states.py           # FSM States
    ├── utils/
    │   ├── __init__.py
    │   ├── database.py     # Database helpers
    │   └── scheduler.py    # Auto-kick scheduler
    ├── handlers/
    │   ├── __init__.py
    │   ├── start.py        # /start command
    │   ├── balance.py      # Balance handlers
    │   ├── plans.py        # Plan purchase
    │   └── admin.py        # Admin panel
    └── main.py             # Main entry point
"""
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        logger.error("Ishlatilish: python client_bot_main.py <bot_token> <bot_name> <owner_id>")
        sys.exit(1)

    bot_token = sys.argv[1]
    bot_name = sys.argv[2]
    owner_id = int(sys.argv[3])

    # Import and run the bot from the modular package
    from client_bot.main import run_bot
    run_bot(bot_token, bot_name, owner_id)
