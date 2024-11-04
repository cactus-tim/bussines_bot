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
            # TODO: here
            logger.exception(str(e))
            return None
        except VacancyNameError as e:
            # TODO: here
            logger.exception(str(e))
            return None
        except NoResultFound as e:
            # TODO: sand that this vacancy doesnt exist
            logger.exception(str(e))
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None
    return wrapper
