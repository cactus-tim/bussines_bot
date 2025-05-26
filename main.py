"""Telegram Bot Main.
Main entry point for the Telegram bot application with router registration and startup logic.
"""

# --------------------------------------------------------------------------------

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import TOKEN
from database.models import async_main
from handlers.admin import admin_routers
from handlers.public import public_routers
from utils.logger import get_logger

# --------------------------------------------------------------------------------

# Initialize logger
logger = get_logger("main")

# Initialize bot and dispatcher
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# --------------------------------------------------------------------------------

def register_routers() -> None:
    """Register all routers in the dispatcher.

    Args:
        None

    Returns:
        None
    """
    # Register public routers
    for router in public_routers:
        dp.include_router(router)
        logger.info(f"Registered public router: {router.name}")

    # Register admin routers
    for router in admin_routers:
        dp.include_router(router)
        logger.info(f"Registered admin router: {router.name}")


# --------------------------------------------------------------------------------

async def main():
    """Start the bot and handle its lifecycle.

    Args:
        None

    Returns:
        None
    """
    try:
        logger.info("Starting bot...")

        await  async_main()

        # Register all routers
        register_routers()
        logger.info("All routers registered successfully")

        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        logger.info("Bot stopped")


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
