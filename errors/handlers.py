import asyncio
from functools import wraps
from sqlalchemy.exc import NoResultFound

from errors.errors import *
from bot_instance import logger, bot


def db_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Error404 as e:
            logger.exception(str(e))
            return None
        except DatabaseConnectionError as e:
            logger.exception(str(e))
            return None
        except Error409 as e:
            logger.exception(str(e))
            return None
        except EventNameError as e:
            logger.exception(str(e))
            return None
        except VacancyNameError as e:
            logger.exception(str(e))
            return None
        except NoResultFound as e:
            logger.exception(str(e))
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None
    return wrapper


def stat_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            user_id = kwargs.get("user_id")
            if not user_id and args:
                user_id = args[0]
            logger.exception(f"Произошла ошибка при выполнении функции {func.__name__}: {str(e)}")
            if user_id:
                await bot.send_message(user_id, "Произошла ошибка при генерации отчета. Пожалуйста, попробуйте позже.")
    return wrapper
