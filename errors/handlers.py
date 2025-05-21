"""
Error Decorators
Wrappers for database and statistic error handling.
"""
# --------------------------------------------------------------------------------
from functools import wraps

from sqlalchemy.exc import NoResultFound

from bot_instance import logger, bot
from errors.errors import (
    DatabaseConnectionError,
    Error404,
    Error409,
    EventNameError,
    VacancyNameError,
)


# --------------------------------------------------------------------------------
def db_error_handler(func):
    """
    Decorator to handle database related exceptions.

    Args:
        func (Callable): Asynchronous function to wrap.

    Returns:
        Callable: Wrapped function that returns original result or None.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (
                Error404,
                DatabaseConnectionError,
                Error409,
                EventNameError,
                VacancyNameError,
                NoResultFound,
        ) as e:
            logger.exception(str(e))
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None

    return wrapper


# --------------------------------------------------------------------------------
def stat_error_handler(func):
    """
    Decorator to handle statistic generation exceptions.

    Args:
        func (Callable): Asynchronous function to wrap.

    Returns:
        Callable: Wrapped function that notifies user on error.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            user_id = kwargs.get("user_id")
            if not user_id and args:
                user_id = args[0]
            logger.exception(
                f"Произошла ошибка при выполнении функции {func.__name__}: {str(e)}"
            )
            if user_id:
                await bot.send_message(
                    user_id,
                    "Произошла ошибка при генерации отчета. Пожалуйста, попробуйте позже."
                )

    return wrapper
