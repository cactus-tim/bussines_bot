"""
Settings module
Application settings and configuration for bot and database.
"""

# --------------------------------------------------------------------------------

import os
from dotenv import load_dotenv

# --------------------------------------------------------------------------------

# Load environment variables from .env file
load_dotenv('.env')

# --------------------------------------------------------------------------------

# Bot settings
TOKEN = os.getenv('TOKEN_API_TG')

# --------------------------------------------------------------------------------

# Environment settings
ENV = os.getenv('ENV', 'development')  # Default to development if not set

# --------------------------------------------------------------------------------

# Database settings
if ENV == 'production':
    """
    Production database configuration using PostgreSQL.
    """

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASS = os.getenv('DB_PASS', '132369')

    SQL_URL = (
        f'postgresql+asyncpg://{DB_USER}:{DB_PASS}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
else:
    """
    Development database configuration using SQLite.
    """

    SQL_URL = "sqlite+aiosqlite:///./database/database.db"

# --------------------------------------------------------------------------------

# Networking settings
NETWORKING_THEMES = ["Локация", "Меню", "Команда", "Маркетинг"]

# --------------------------------------------------------------------------------

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
