import pytest
from PyChart import PseudoCode
from Py2PseudoCode import Py2PseudoCode  # Замените на фактический путь


@pytest.mark.parametrize("input_code, expected", [
    # Простое арифметическое выражение с возведением в степень
    ("a = b ** 2", "a = b ^ 2\n"),

    # Упрощённое выражение с += и -=
    ("x += 1", "x = x + 1\n"),
    ("y -= 2", "y = y - 2\n"),

    # Импорт должен быть удалён
    ("import math", ""),

    # Приведение типов должно быть удалено
    ("x = int(input())", "x =input()\n"),
    ("y = float(3.14)", "y =3.14\n"),

    # Выражения print должны быть упрощены
    ("print(5)", "5\n"),
    ("print(int(x))", "int(x)\n"),

    # Условия
    ("if a > b:", "a > b\n"),
    ("elif a == b:", "a == b\n"),
    ("else:", ""),

    # Цикл for с range
    ("for i in range(1, 5):", "i <= 5\n"),

    # Цикл while
    ("while x < 10:", "x < 10\n"),

    # Объявление функции
    ("def my_function(a, b):", "function my_function\n"),

    # Просто строка
    ("z = a + b", "z = a + b\n"),
])
def test_to_pseudocode(input_code, expected):
    result = Py2PseudoCode.to_pseudocode(input_code)
    assert result == expected
