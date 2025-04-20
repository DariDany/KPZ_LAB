import pytest
from PyChart import BlockDiagram
from Py2BlockDiagram import Py2BlockDiagram  # Замените на ваш актуальный модуль

# Тесты для _get_struct_type


@pytest.mark.parametrize("line, expected", [
    ("if x > 0:", "if"),
    ("elif x == 0:", "elif"),
    ("else:", "else"),
    ("for i in range(5):", "loop"),
    ("while True:", "loop"),
    ("def my_func():", "function"),
    ("print('Hello')", "output"),
    ("x = 5", "block"),
])
def test_get_struct_type(line, expected):
    assert Py2BlockDiagram._get_struct_type(line) == expected


# Тесты для _get_bd_type_of_line

@pytest.mark.parametrize("line, expected", [
    ("for i in range(10):", "Logical Operator"),
    ("while x < 5:", "Logical Operator"),
    ("if x > 0:", "Logical Operator"),
    ("elif y == 2:", "Logical Operator"),
    ("x > y ? x : y", "Logical Operator"),
    ("print('Hello')", "Input / Output"),
    ("x = input()", "Input / Output"),
    ("output = y", "Input / Output"),
    ("start", "Start / end"),
    ("end", "Start / end"),
    ("x = 10", "Block"),
    ("result = a + b", "Block"),
    ("unknown line", "Block"),
])
def test_get_bd_type_of_line(line, expected):
    assert Py2BlockDiagram._get_bd_type_of_line(line) == expected
