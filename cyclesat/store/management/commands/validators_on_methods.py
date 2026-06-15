"""Функции для проверки данных при импорте из CSV."""

from datetime import datetime

from django.core.validators import validate_email, validate_slug

from store.management.commands.exceptions import (
    EmptyFieldError,
    IncorrectYearError,
    InvalidDateTimeFormatError,
    InvalidEmailError,
    InvalidSlugError,
    NotNumberError,
    NotUniqueIDError
)


class ValidatorCSV:
    """Класс для валдиации данных в CSV-формате.

    Содержит методы проверки:
        - на пустые данные (для обязательных полей),
        - на целочесленные данные (для цеочисленных полей),
        - на уникальность (для полей с уникальными значениями),
        - на корректность слага,
        - на корректность e-mail,
        - на соответствие формата даты необходимому паттерну,
        - на превышение заданного (текущего) года,
        - на корректность оценки для заданной шкалы.
    Помимо методов проверки содержит служебные методы:
        - для транспонирования данных,
        - для иттерирования данных,
        - для составления отчета о проверке.
    """

    def __init__(self):
        """Конструктор."""
        pass

    @staticmethod
    def data_transponse(
        data: list[dict[str, str]]
    ) -> dict[str, list[str]]:
        """Метод транспонирования списка словарей в словарь списков.

        Принимает: список словарей из CSV-файла.
        Возвращает: словарь списокв с ключами из имен полей модели.
        """
        transponse_data = {}
        for row in data:
            for key, value in row.items():
                if key not in transponse_data.keys():
                    transponse_data |= {key: [value]}
                    continue
                transponse_data[key].append(value)

        return transponse_data

    @staticmethod
    def check_by_fields(
        check_pattern, data, *args
    ) -> dict[str, list[tuple[int, str]]]:
        """Метод проверки записей по полям.

        Принимает:
            - паттерн проверки из конкретного проверочного метода,
            - список данных из CSV-файла,
            - имена полей для проверки.
        Если поля не указаны, то проверка идет по всем полям.
        Для удобства иттерирования по полям модели данные транспонируются.
        К данным применяется паттерн проверки из методы проверки.
        При наличии ошибок возвращает список кортежей, в которых:
            - первый элемент - номер строки с некорретными данными,
            - второй элемент - собственно некорректные данные.
        """
        data = __class__.data_transponse(data)
        if not args:
            args = tuple(key for key in data.keys() if not args)
        err_dict = {}

        for key, value in data.items():
            if key in args:
                err_list = []
                for ind, el in enumerate(value, 2):
                    try:
                        if not check_pattern(el, value):
                            err_list.append((ind, el))
                    except Exception:
                        err_list.append((ind, el))
                    if err_list:
                        err_dict[key] = err_list
            continue

        return err_dict

    @staticmethod
    def print_report(err_dict, err_message):
        """Метод составления отчета о проверке.

        Принимает:
            - список (с ошибками),
            - сообщение о типе ошибки.
        Если список непустой, выводит в консоли подробный отчет с некорректными
        значениями и их координатами в CSV-файле (столбец и строка).
        Строка - это строка CSV-файла, т.е. начиная со 2-ой.
        """
        if err_dict:
            print('ERROR')
            print(f'{err_message}')
            for i, (col, err_in_col) in enumerate(err_dict.items(), 1):
                ext_tree_branch = '└──' if i == len(err_dict) else '├──'
                int_tree_branch = '    ' if i == len(err_dict) else '│   '
                print(f'{ext_tree_branch} поле {col}:')
                for i, err in enumerate(err_in_col, 1):
                    tree_branch = '└──' if i == len(err_in_col) else '├──'
                    print(
                        f'{int_tree_branch}{tree_branch} ',
                        f'строка {err[0]}: {err[1]}'
                    )
            return
        print('OK')
        return

    @classmethod
    def not_empty_check(cls, data: list[dict[str, str]], *args: tuple[str]):
        """Метод проверки пустых полей.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
        Если поля не указаны, то проверка идет по всем полям.
        """
        print('проверка пустых данных... ', end="", flush=True)

        def not_empty_check_pattern(el, value):
            return el.strip()

        check_pattern = not_empty_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'отсутсвует содержимое:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise EmptyFieldError('Ошибка данных: обнаружены пустые записи.')

    @classmethod
    def integer_check(cls, data: list[dict[str, str]], *args: tuple[str]):
        """Метод проверки числовых полей.

        Проверяет возможность преобразования данных в целое число.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
        Если поля не указаны, то проверка идет по всем полям.
        """
        print('проверка числовых данных... ', end="", flush=True)

        def integer_check_pattern(el, value):
            return isinstance(int(el), int)

        check_pattern = integer_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'нецелочисленные данные:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise NotNumberError(
                'Ошибка данных: обнаружены нецелочисленные записи.'
            )

    @classmethod
    def unique_check(cls, data: list[dict[str, str]], *args: tuple[str]):
        """Метод проверки записей на уникальность.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
        Если поля не указаны, то проверка идет по всем полям.
        """
        print('проверка уникальных полей... ', end="", flush=True)

        def unique_check_pattern(el, value):
            ind = value.index(el)
            delta = 1
            while ind + delta < len(value):
                if el == value[ind + delta]:
                    return False
                delta += 1
            return True

        check_pattern = unique_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'неуникальные записи:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise NotUniqueIDError(
                'Ошибка данных: обнаружены повторяющиеся записи.'
            )

    @classmethod
    def slug_check(cls, data: list[dict[str, str]], *args: tuple[str]):
        """Метод проверки слага.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
        Если поля не указаны, то проверка идет по всем полям.
        """
        print('проверка занчений слагов... ', end="", flush=True)

        def slug_check_pattern(el, value):
            return not validate_slug(el)

        check_pattern = slug_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'недопустимые символы в слаге:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise InvalidSlugError(
                'Ошибка данных: некорретный слаг.'
            )

    @classmethod
    def email_check(cls, data: list[dict[str, str]], *args: tuple[str]):
        """Метод проверки email.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
        Если поля не указаны, то проверка идет по всем полям.
        """
        print('проверка полей email... ', end="", flush=True)

        def email_check_pattern(el, value):
            return not validate_email(el)

        check_pattern = email_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'недопустимые символы в email:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise InvalidEmailError(
                'Ошибка данных: некорретный email.'
            )

    @classmethod
    def date_check(
        cls,
        data: list[dict[str, str]],
        *args: tuple[str],
        datetime_pattern: str = None
    ):
        """Метод проверки формата даты.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить,
            - паттерн для проверки даты (необязательный аргумент).
        Если поля не указаны, то проверка идет по всем полям.
        Если паттерн не указаны, то проверяет на соответствие паттерну
        "%Y-%m-%dT%H:%M:%S.%fZ".
        """
        print('проверка корректности даты... ', end="", flush=True)

        def date_check_pattern(el, value):
            if datetime_pattern is None:
                return datetime.strptime(el, "%Y-%m-%dT%H:%M:%S.%fZ")
            return datetime.strptime(el, datetime_pattern)

        check_pattern = date_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'некорректный формат даты:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise InvalidDateTimeFormatError(
                'Ошибка данных: некорретный формат даты.'
            )

    @classmethod
    def year_no_more_check(
        cls,
        data: list[dict[str, str]],
        *args: tuple[str],
        max_year: int = None
    ):
        """Метод проверки года.

        Проверяет, чтобы значение года было в допустимом диапазоне.

        Принимает:
            - данные для проверки из CSV-файла в виде списка словарей,
            - имена полей, данные в которых нужно проверить.
            - максимальное возможное значение года (необязательный аргумент),
        Если поля не указаны, то проверка идет по всем полям.
        Если верхняя граница года не указана, то проверяет, чтобы год
        не превышал текущий на момент проверки.
        """
        print('проверка корректности года... ', end="", flush=True)

        def year_check_pattern(el, value):
            if max_year is not None:
                return int(el) <= max_year
            return int(el) <= datetime.now().year

        check_pattern = year_check_pattern
        err_dict = cls.check_by_fields(check_pattern, data, *args)
        err_message = 'некорректный формат года:'
        cls.print_report(err_dict, err_message)
        if err_dict:
            raise IncorrectYearError(
                'Ошибка данных: товар из будущего.'
            )
