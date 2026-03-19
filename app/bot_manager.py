import asyncio
import logging
from typing import Dict
from client_bot.main import start_client_bot

logger = logging.getLogger(__name__)

# Dictionary to hold running bot tasks
# Key: bot_token, Value: asyncio.Task
active_bot_tasks: Dict[str, asyncio.Task] = {}

async def run_bot_in_background(bot_token: str, bot_username: str, owner_id: int):
    """Starts a bot in a background asyncio task if not already running."""
    if bot_token in active_bot_tasks and not active_bot_tasks[bot_token].done():
        logger.info(f"Bot {bot_username} is already running.")
        return active_bot_tasks[bot_token]

    logger.info(f"Starting bot task for {bot_username}...")
    task = asyncio.create_task(start_client_bot(bot_token, bot_username, owner_id))
    active_bot_tasks[bot_token] = task
    
    # Callback to remove from dict when finished
    def _on_done(t):
        if active_bot_tasks.get(bot_token) == t:
            active_bot_tasks.pop(bot_token, None)
            
    task.add_done_callback(_on_done)
    return task

def stop_bot_task(bot_token: str):
    """Cancels a bot's running task."""
    task = active_bot_tasks.pop(bot_token, None)
    if task and not task.done():
        logger.info(f"Cancelling bot task for token {bot_token[:10]}...")
        task.cancel()
        return True
    return False

def is_bot_running(bot_token: str) -> bool:
    return bot_token in active_bot_tasks and not active_bot_tasks[bot_token].done()
