"""
Database Models Package

SQLAlchemy ORM models for:
- User: Bot subscribers/users
- Client: Bot creators/owners
- ClientBot: Created bot instances
- Transaction: Payment records
- Spending: Balance deduction records
- DeletedBot: Deleted bots archive
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to ensure they're registered
from app.models.user import User
from app.models.client import Client
from app.models.client_bot import ClientBot
from app.models.transaction import Transaction
from app.models.spending import Spending
from app.models.deleted_bot import DeletedBot

__all__ = ["Base", "User", "Client", "ClientBot", "Transaction", "Spending", "DeletedBot"]
