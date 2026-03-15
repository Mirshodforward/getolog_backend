from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv
import os
import pytz

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    BOT_TOKEN: str = ""
    DATABASE_URL: str = ""
    DEV_MODE: bool = False
    CARD_NUMBER: str = ""
    ADMIN_ID: str = ""  # Keep as string initially
    PREMIUM_PRICE: int = 67000
    
    # Plan pricing
    FREE_PLAN_PRICE: int = 0
    STANDARD_PLAN_PRICE: int = 97000
    BIZNES_PLAN_PRICE: int = 497000
    
    # Plan bot limits
    FREE_PLAN_BOT_LIMIT: int = 1
    STANDARD_PLAN_BOT_LIMIT: int = 2
    BIZNES_PLAN_BOT_LIMIT: int = 5

    @field_validator("ADMIN_ID", mode="after")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v:
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return []

settings = Settings()

# Convert ADMIN_ID string to list after initialization
if isinstance(settings.ADMIN_ID, str):
    settings.ADMIN_ID = [int(x.strip()) for x in settings.ADMIN_ID.split(",") if x.strip()]

# Plan configuration mapping
PLAN_CONFIG = {
    "free": {
        "name": "Free",
        "price": settings.FREE_PLAN_PRICE,
        "bot_limit": settings.FREE_PLAN_BOT_LIMIT,
    },
    "standard": {
        "name": "Standard",
        "price": settings.STANDARD_PLAN_PRICE,
        "bot_limit": settings.STANDARD_PLAN_BOT_LIMIT,
    },
    "biznes": {
        "name": "Biznes",
        "price": settings.BIZNES_PLAN_PRICE,
        "bot_limit": settings.BIZNES_PLAN_BOT_LIMIT,
    }
}

# Timezone
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

# Default language
DEFAULT_LANGUAGE = "uz"
