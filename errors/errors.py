class CustomError(Exception):
    pass


class DatabaseConnectionError(CustomError):
    def __init__(self, message="Error with connection to db"):
        self.message = message
        super().__init__(self.message)


class Error404(CustomError):
    def __init__(self, message="Error with status code 404"):
        self.message = message
        super().__init__(self.message)


class Error409(CustomError):
    def __init__(self, message="Error with status code 409"):
        self.message = message
        super().__init__(self.message)


class EventNameError(CustomError):
    def __int__(self, message="Событие с таким названием уже существует"):
        self.message = message
        super().__init__(self.message)


class VacancyNameError(CustomError):
    def __int__(self, message="Вакансия с таким названием уже существует"):
        self.message = message
        super().__init__(self.message)
