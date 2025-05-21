"""
Bot Instance
Initialize Telegram bot and environment configuration.
"""

# --------------------------------------------------------------------------------
import asyncio
import logging
import os
import sys

# --------------------------------------------------------------------------------
# Add local lida module to path
sys.path.append(os.path.join(sys.path[0], 'lida'))

# --------------------------------------------------------------------------------
# Load environment variables
from dotenv import load_dotenv

load_dotenv('.env')

# --------------------------------------------------------------------------------
# Configuration constants
token = os.getenv('TOKEN_API_TG')
SQL_URL_RC = (
    f'postgresql+asyncpg://{os.getenv("DB_USER")}:'
    f'{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:'
    f'{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
)

# --------------------------------------------------------------------------------
# Initialize Bot instance
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

# --------------------------------------------------------------------------------
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------
# Global asyncio event
event = asyncio.Event()
