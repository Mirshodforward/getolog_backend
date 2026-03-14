"""
Client Bot Configuration
"""
import os
import logging
from dotenv import load_dotenv
from pytz import timezone as pytz_timezone

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("client_bot")

# Timezone: UTC+5 (Tashkent)
TIMEZONE = pytz_timezone('Asia/Tashkent')

# Reklama text for free clients
REKLAMA_TEXT = os.getenv('REKLAMA_TEXT', 'Bu bot @darslinker_bot tomonidan ishlab chiqilgan.')
