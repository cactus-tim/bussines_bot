"""
App Entrypoint
Initialize and run the Telegram bot application.
"""
# --------------------------------------------------------------------------------
import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_instance import bot
from confige import BotConfig
from database.models import async_main
from handlers import admin, error, quest, user  # Router modules


# --------------------------------------------------------------------------------
def register_routers(dp: Dispatcher) -> None:
    """
    Include all routers into dispatcher.

    Args:
        dp (Dispatcher): Dispatcher instance to register routers on.

    Returns:
        None
    """
    dp.include_routers(admin.router, quest.router, error.router, user.router)


# --------------------------------------------------------------------------------
async def main() -> None:
    """
    Run application: initialize DB, configure bot, and start polling.

    Returns:
        None
    """
    # Initialize database models and connections
    await async_main()

    # Create bot configuration and dispatcher
    config = BotConfig(
        admin_ids=[],  # List administrator IDs
        welcome_message="",  # Initial welcome message
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    # Register all routers
    register_routers(dp)

    # Start the bot polling loop
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as ex:
        print(f"Exception: {ex}")


# --------------------------------------------------------------------------------
if __name__ == '__main__':
    asyncio.run(main())
