"""
Getolog Bot - Main Application Package

This is the main Telegram bot for managing client bots.
Provides bot creation, user management, and payment processing.

Modules:
- config: Application settings
- database: Database connection and session management
- models: SQLAlchemy ORM models
- crud: Database operations
- states: FSM states for conversation flow
- handlers: Message and callback handlers
"""
from app.config import settings
from app.database import engine, AsyncSessionLocal
from app.models import Base

__all__ = ["settings", "engine", "AsyncSessionLocal", "Base"]
