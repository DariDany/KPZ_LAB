
import pytest
from PyChart import BlockDiagram

# Фейкова реалізація абстрактного класу


class TestableBlockDiagram(BlockDiagram):
    def _get_struct_type(self, line: str) -> str:
        if 'if ' in line:
            return 'if'
        if 'else' in line:
            return 'else'
        if 'for ' in line or 'while ' in line:
            return 'loop'
        if 'print' in line or '=' in line:
            return 'output'
        return 'block'

    def _get_bd_type_of_line(self, line: str) -> str:
        if 'if' in line or 'else' in line:
            return 'Logical Operator'
        if 'for' in line or 'while' in line:
            return 'Цикл for'
        if 'print' in line:
            return 'Ввод / вывод'
        return 'Блок'

# Простий фейковий конвертер у псевдокод


class DummyPseudocodeConverter:
    def to_pseudocode(self, line: str) -> str:
        return line  # no conversion


@pytest.fixture
def diagram_builder():
    def _build(code_tree):
        return TestableBlockDiagram(
            pseudocode=DummyPseudocodeConverter(),
            code_tree=code_tree,
            variables=[],
            name='main'
        )
    return _build


def test_basic_block_creation(diagram_builder):
    diagram = diagram_builder(["a = 5", "print(a)"]).build()
    assert any("a = 5" in b['code'] for b in diagram['blocks'])
    assert any("print(a)" in b['code'] for b in diagram['blocks'])
    assert len(diagram['arrows']) == 3  # Start → a=5 → print(a)-> End


def test_if_else_connection(diagram_builder):
    code = [
        {"if a > 0:": [
            "print('positive')"
        ]},
        {"else:": [
            "print('not positive')"
        ]},
        "print('done')"
    ]
    diagram = diagram_builder(code).build()
    arrows = diagram['arrows']
    assert any(a['label'] == 'так' for a in arrows)
    assert any(a['label'] == 'ні' for a in arrows)


def test_for_loop_with_increment(diagram_builder):
    code = [
        {"for i in range(0, n):": [
            "print(i)"
        ]},
        "print('done')"
    ]
    diagram = diagram_builder(code).build()
    texts = [b['text'] for b in diagram['blocks']]
    assert "i = i + 1" in texts
    assert any(a['label'] == 'ні' for a in diagram['arrows'])
    assert any(a['label'] == 'так' for a in diagram['arrows'])


def test_nested_loops(diagram_builder):
    code = [
        {"for i in range(0, 3):": [
            {"for j in range(0, 2):": [
                "print(i, j)"
            ]}
        ]}
    ]
    diagram = diagram_builder(code).build()
    texts = [b['text'] for b in diagram['blocks']]
    assert "i = i + 1" in texts
    assert "j = j + 1" in texts
    assert len([a for a in diagram['arrows'] if a['label'] == 'так']) >= 2
    assert len([a for a in diagram['arrows'] if a['label'] == 'ні']) >= 2


def test_while_loop(diagram_builder):
    code = [
        {"while x < 5:": [
            "x = x + 1"
        ]},
        "print('end')"
    ]
    diagram = diagram_builder(code).build()
    assert any(b['text'] == "x = x + 1" for b in diagram['blocks'])
    assert any(a['label'] == 'так' for a in diagram['arrows'])
    assert any(a['label'] == 'ні' for a in diagram['arrows'])
