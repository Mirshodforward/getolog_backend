from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import pytz

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DEV_MODE: bool = os.getenv("DEV_MODE", "false").lower() == "true"
    CARD_NUMBER: str = os.getenv("CARD_NUMBER")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID"))
    PREMIUM_PRICE: int = int(os.getenv("PREMIUM_PRICE", "67000"))

    class Config:
        env_file = ".env"
        extra = "ignore"  # Extra fields-ni ignore qil

settings = Settings()

# Timezone
TASHKENT_TZ = pytz.timezone('Asia/Tashkent')

# Default language
DEFAULT_LANGUAGE = "uz"
