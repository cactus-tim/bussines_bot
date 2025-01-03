import asyncio
import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from confige import BotConfig
from datetime import datetime, timedelta
from pytz import timezone

from bot_instance import bot
from handlers import user, error, admin, quest
from database.models import async_main


def register_routers(dp: Dispatcher) -> None:
    dp.include_routers(admin.router, quest.router, error.router, user.router)


async def main() -> None:
    await async_main()

    config = BotConfig(
        admin_ids=[],
        welcome_message=""
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    register_routers(dp)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')


if __name__ == '__main__':
    asyncio.run(main())