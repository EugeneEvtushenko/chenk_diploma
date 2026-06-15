"""Модуль с кастомными исключениями."""


class EmptyFieldError(Exception):
    """Исключение если найдены пустые записи."""


class NotNumberError(Exception):
    """Исключение если данные не являются числом."""


class NotUniqueIDError(Exception):
    """Исключение на случай неуникального ID."""


class InvalidSlugError(Exception):
    """Исключение на случай невалидного слага."""


class InvalidEmailError(Exception):
    """Исключение на случай невалидного Email."""


class InvalidDateTimeFormatError(Exception):
    """Исключение на случай некорректного формата даты."""


class IncorrectYearError(Exception):
    """Исключение на случай превышения текущего года."""
