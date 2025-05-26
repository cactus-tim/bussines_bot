"""
Telegram Errors
Global error and safe message handlers for bot.
"""
# --------------------------------------------------------------------------------
import asyncio

import requests
from aiogram import types, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientConnectorError

from config.settings import TOKEN
from keyboards.keyboards import single_command_button_keyboard
from utils.logger import get_logger

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)
logger = get_logger("main")



# --------------------------------------------------------------------------------
async def safe_send_message(
        bott: Bot,
        recipient,
        text: str,
        reply_markup=single_command_button_keyboard(),
        retry_attempts: int = 3,
        delay: int = 5,
) -> Message | None:
    """
    Send message with retry and error handling.

    Args:
        bott (Bot): Bot instance to send message.
        recipient (Message|CallbackQuery|int): Message recipient.
        text (str): Message text.
        reply_markup: Reply keyboard markup.
        retry_attempts (int): Max retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        Message|None: Sent message or None if failed.
    """
    for attempt in range(retry_attempts):
        try:
            if isinstance(recipient, types.Message):
                msg = await recipient.answer(
                    text, reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif isinstance(recipient, types.CallbackQuery):
                msg = await recipient.message.answer(
                    text, reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            elif isinstance(recipient, int):
                msg = await bott.send_message(
                    chat_id=recipient, text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                raise TypeError(
                    f"Неподдерживаемый тип recipient: {type(recipient)}"
                )
            return msg
        except ClientConnectorError as e:
            logger.error(
                f"Ошибка подключения: {e}. Попытка {attempt + 1} "
                f"из {retry_attempts}."
            )
            if attempt < retry_attempts - 1:
                await asyncio.sleep(delay)
                return None
            else:
                logger.error(
                    f"Не удалось отправить сообщение после "
                    f"{retry_attempts} попыток."
                )
                return None
        except Exception as e:
            logger.error(str(e))
            return None
    return None


# --------------------------------------------------------------------------------
async def make_short_link(url: str) -> str | None:
    """
    Create short link using clck.ru service.

    Args:
        url (str): URL to shorten.

    Returns:
        str|None: Short link or None if failed.
    """
    try:
        response = requests.post(
            'https://clck.ru/--', data={'url': url}
        )
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        logger.error(str(e))
        return None

async def get_bot_username():
    return  (await bot.get_me()).username