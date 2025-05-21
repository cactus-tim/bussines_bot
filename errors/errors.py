"""
Custom Errors
Custom exceptions for database and event/vacancy validations.
"""


# --------------------------------------------------------------------------------
class CustomError(Exception):
    """
    Base class for custom exceptions.

    Args:
        message (str): Error message.
    """
    pass


# --------------------------------------------------------------------------------
class DatabaseConnectionError(CustomError):
    """
    Exception raised for database connection errors.

    Args:
        message (str): Description of the connection error.
    """

    def __init__(self, message: str = "Error with connection to db"):
        super().__init__(message)
        self.message = message


# --------------------------------------------------------------------------------
class Error404(CustomError):
    """
    Exception raised for HTTP 404 not found errors.

    Args:
        message (str): Description of the 404 error.
    """

    def __init__(self, message: str = "Error with status code 404"):
        super().__init__(message)
        self.message = message


# --------------------------------------------------------------------------------
class Error409(CustomError):
    """
    Exception raised for HTTP 409 conflict errors.

    Args:
        message (str): Description of the 409 error.
    """

    def __init__(self, message: str = "Error with status code 409"):
        super().__init__(message)
        self.message = message


# --------------------------------------------------------------------------------
class EventNameError(CustomError):
    """
    Exception raised when an event name already exists.

    Args:
        message (str): Description of the event name error.
    """

    def __int__(self, message: str = "Событие с таким названием уже существует"):
        super().__init__(message)
        self.message = message


# --------------------------------------------------------------------------------
class VacancyNameError(CustomError):
    """
    Exception raised when a vacancy name already exists.

    Args:
        message (str): Description of the vacancy name error.
    """

    def __int__(self, message: str = "Вакансия с таким названием уже существует"):
        super().__init__(message)
        self.message = message
