from typing import Iterable
from abc import ABC, abstractmethod


class Preprocessor(ABC):
    def __init__(self, file: Iterable) -> None:
        # Зберігаємо вміст файлу
        self._file = file
        # Список для збереження обробленого (очищеного) коду
        self._parsed_code = []
        # Парсимо вхідний файл (видаляємо коментарі)
        self._parse()
        # Сереалізуємо код — перетворюємо у зручну структуру (словник з заголовками та тілами блоків)
        self._serealized_code = self._get_serealized_code(self._parsed_code)

    @abstractmethod
    def _parse(self) -> list:
        """
        Метод для парсингу коду з файлу — видаляє коментарі та повертає список рядків коду.

        Повертає:
            Список рядків без коментарів.
        """
        pass

    @abstractmethod
    def _get_serealized_code(self, code: list) -> list:
        """
        Метод серіалізації коду — створює структуру типу:
        {'if n == 1:': ['n+=2', 'print(n)']}

        Аргументи:
            code: список рядків обробленого коду

        Повертає:
            Список або словник серіалізованого коду
        """
        pass

    @abstractmethod
    def _cut_functions(self, serealized_code: list):
        """
        Метод вирізає всі функції з серіалізованого коду і повертає їх.

        Аргументи:
            serealized_code: серіалізований код, з якого видаляються функції

        Повертає:
            Список словників з іменами функцій та їх тілом
        """
        pass

    @abstractmethod
    def _get_function_name(self, line: str):
        """
        Метод для отримання імені функції з її оголошення

        Аргументи:
            line: рядок з оголошенням функції
        """
        pass

    @abstractmethod
    def _find_all_veribles(self, code: list) -> list:
        """
        Метод для пошуку всіх змінних у переданому коді.
        Вхідний список не змінюється.

        Аргументи:
            code: список рядків обробленого або серіалізованого коду
        """
        pass

    def get_programs_list(self) -> list:
        # Отримуємо головний (основний) код програми
        main = self._serealized_code
        # Отримуємо всі функції, вирізавши їх з основного коду
        functions = self._cut_functions(main)
        programs_list = []

        # Опрацьовуємо кожну функцію
        for fun in functions:
            fun = fun.copy()
            body = list(fun.values())[0]
            head = list(fun.keys())[0]

            # Знаходимо змінні у тілі функції
            variables = self._find_all_veribles(body)
            # Отримуємо ім'я функції
            name = self._get_function_name(head)
            # Додаємо аргументи функції до списку змінних
            variables += self._get_fun_args(head, name)

            # Додаємо функцію до загального списку програм
            programs_list.append(
                {'code': body, 'name': name, 'variables': variables})

        # Якщо функції main немає серед оброблених
        for p in programs_list:
            if p['name'] == 'main':
                break
        else:
            # Якщо залишився основний код, додаємо його як main
            if main:
                programs_list.append(
                    {'code': main, 'name': 'main', 'variables': self._find_all_veribles(main)})
            return programs_list

        # Вивід для дебагу серіалізованого main
        print("Serialized main:", main)
        return programs_list

    @abstractmethod
    def _get_fun_args(self, line: str, fun_name='') -> list:
        """
        Метод для отримання аргументів функції за її заголовком.

        Аргументи:
            line: рядок з оголошенням функції
            fun_name: ім'я функції (необов'язкове)

        Повертає:
            Список аргументів функції
        """
        pass
