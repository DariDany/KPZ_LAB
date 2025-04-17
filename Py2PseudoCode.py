import re
from PyChart import PseudoCode


class Py2PseudoCode(PseudoCode):

    @staticmethod
    def to_pseudocode(lines: str) -> str:
        pseudocode = ''
        lines = lines.split('\n')  # type: ignore

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Заміна ** на ^
            line = line.replace('**', '^')

            # Приведення -= і += до повноцінного вигляду
            line = re.sub(r'(\w+)\s*\-=\s*(.+)', r'\1 = \1 - \2', line)
            line = re.sub(r'(\w+)\s*\+=\s*(.+)', r'\1 = \1 + \2', line)

            # Видалити імпорти
            if 'import ' in line:
                continue

            # print(int(...)) або print(...) → просто вираз
            line = re.sub(r'print\s*\((.*)\)', r'\1', line)

            # input, int(...), float(...) тощо — прибирати приведення типу
            line = re.sub(r'(\=| |\()(int|float|str|bool|tuple|list|dict|set)\s*\((.*?)\)', r'\3', line)

            # Розбір структур керування
            if line.startswith('if '):
                condition = re.sub(r'^if\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'
            elif line.startswith('elif '):
                condition = re.sub(r'^elif\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'
            elif line.startswith('else'):
                pseudocode += ''
            elif line.startswith('for '):
                # for i in range(...) → i in range(...)
                match = re.match(r'for\s+(\w+)\s+in\s+(.*):', line)
                if match:
                    var, rng = match.groups()
                    pseudocode += f'{var} in {rng}\n'
                else:
                    pseudocode += line.rstrip(':') + '\n'
            elif line.startswith('while '):
                condition = re.sub(r'^while\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'
            elif line.startswith('def '):
                func_name = re.sub(r'^def\s+(\w+)\s*\(.*\):$', r'\1', line)
                pseudocode += f'function {func_name}\n'
            else:
                # Усі інші рядки — як є
                pseudocode += line + '\n'

        return pseudocode
