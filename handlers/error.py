"""
Telegram Errors
Global error and safe message handlers for bot.
"""
# --------------------------------------------------------------------------------
import asyncio

from aiogram import Router, types, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest, TelegramRetryAfter,
    TelegramUnauthorizedError, TelegramNetworkError,
)

from config.settings import TOKEN
from handlers.utils.base import safe_send_message
from utils.logger import get_logger

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)
logger = get_logger("main")

router = Router()


# --------------------------------------------------------------------------------
@router.errors()
async def global_error_handler(event: types.Update, exception: Exception) -> bool:
    """
    Handle global bot exceptions.

    Args:
        event (types.Update): Incoming update instance.
        exception (Exception): Raised exception.

    Returns:
        bool: True if exception was handled.
    """
    if isinstance(exception, TelegramBadRequest):
        if "message can't be edited" in str(exception):
            # Ignore message edit errors as we handle them in the mailing functions
            return True
        logger.error(
            f"Некорректный запрос: {exception}. Пользователь: "
            f"{event.message.from_user.id if event.message else 'Unknown'}"
        )
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logger.error(
            f"Request limit exceeded. Retry after {exception.retry_after} "
            "seconds."
        )
        await asyncio.sleep(exception.retry_after)
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logger.error(f"Authorization error: {exception}")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logger.error(f"Network error: {exception}")
        await asyncio.sleep(5)
        if event.message:
            await safe_send_message(
                bot,
                event.message.chat.id,
                text="Повторная попытка..."
            )
        return True
    else:
        logger.exception(f"Неизвестная ошибка: {exception}")
        return True
