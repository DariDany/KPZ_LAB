import pytest
from unittest.mock import MagicMock
from PyPreprocessor import PyPreprocessor  # Замените на ваш модуль


class DummyPreprocessor(PyPreprocessor):
    def __init__(self, file_lines):
        self._file = file_lines
        self._parsed_code = []


@pytest.fixture
def preprocessor():
    return DummyPreprocessor([
        "def my_func(x):\n",
        "    if x > 0:\n",
        "        print(x)\n",
        "    # this is comment\n",
        "    return x\n"
    ])


def test_parse_removes_comments_and_handles_colons(preprocessor):
    preprocessor._parse()
    expected = [
        "def my_func(x):\n",
        "    if x > 0:\n",
        "        print(x)\n",
        "    return x\n"
    ]
    assert len(preprocessor._parsed_code) == 4
    assert all("#" not in line for line in preprocessor._parsed_code)


def test_get_level_of_line():
    assert PyPreprocessor._get_level_of_line("        x = 5") == 2
    assert PyPreprocessor._get_level_of_line("x = 5") == 0


def test_increase_level_of_line():
    line = "    x = 10"
    assert PyPreprocessor._increase_level_of_line(line, 1) == "        x = 10"


def test_set_level_of_line():
    assert PyPreprocessor._set_level_of_line("x = 10", 2) == "        x = 10"


def test_find_end_of_body():
    processor = DummyPreprocessor([
        "if x:\n",
        "    y = 1\n",
        "    z = 2\n",
        "a = 5\n"
    ])
    assert processor._find_end_of_body(processor._file, 0) == 2


def test_is_control_structure():
    assert PyPreprocessor._is_control_structure("if x > 0:")
    assert PyPreprocessor._is_control_structure("for i in range(5):")
    assert not PyPreprocessor._is_control_structure("x = 5")


def test_get_function_name():
    processor = DummyPreprocessor([])
    assert processor._get_function_name("def test_func(a, b):") == "test_func"


def test_get_fun_args():
    line = "def test_func(a, b=2, c=[1,2]):"
    fun_name = "test_func"
    dummy = DummyPreprocessor([])
    args = dummy._get_fun_args(line, fun_name)
    assert args == ["a", "b=2", "c=[1,2]"]


def test_find_all_variables_flat():
    processor = DummyPreprocessor([])
    processor._parsed_code = [
        "x = 5",
        "y = x + 2",
        "for i in range(10):",
        "    z = i",
        "while k < 5:",
        "    m = k"
    ]
    result = processor._find_all_veribles()
    assert set(result) >= {"x", "y", "i", "z", "k", "m"}


def test_cut_functions_extraction():
    code = [
        {"def my_func():": [
            "x = 1",
            {"def nested():": ["y = 2"]},
            "return x"
        ]},
        "a = 5"
    ]
    preprocessor = DummyPreprocessor([])
    cut = preprocessor._cut_functions(code)
    names = [list(f.keys())[0] for f in cut]
    assert "def my_func():" in names
    assert "def nested():" in names


def test_get_serealized_code():
    processor = DummyPreprocessor([
        "if x:\n",
        "    y = 1\n",
        "    z = 2\n",
        "a = 5\n"
    ])
    result = processor._get_serealized_code(processor._file)
    assert isinstance(result[0], dict)
    assert result[1] == "a = 5"
