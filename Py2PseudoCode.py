import re
from PyChart import PseudoCode


class Py2PseudoCode(PseudoCode):

    @staticmethod
    def to_pseudocode(lines: str) -> str:
        pseudocode = ''
        lines = lines.split('\n')  # Розбиваємо вхідний текст на окремі рядки

        for line in lines:
            line = line.strip()  # Видаляємо зайві пробіли з початку та кінця рядка

            if not line:
                continue  # Пропускаємо порожні рядки

            # Заміна оператора піднесення до степеня Python (** → ^)
            line = line.replace('**', '^')

            # Перетворення скорочених форм -= та += у повну форму
            line = re.sub(r'(\w+)\s*\-=\s*(.+)', r'\1 = \1 - \2', line)
            line = re.sub(r'(\w+)\s*\+=\s*(.+)', r'\1 = \1 + \2', line)

            # Видаляємо рядки з імпортами, бо вони не мають значення у псевдокоді
            if 'import ' in line:
                continue

            # Перетворення команди print(...) на просто вираз (без виводу)
            line = re.sub(r'print\s*\((.*)\)', r'\1', line)

            # Прибираємо приведення типів (int(...), float(...), тощо)
            line = re.sub(
                r'(\=| |\()(int|float|str|bool|tuple|list|dict|set)\s*\((.*?)\)', r'\3', line)

            # Обробка умовних операторів
            if line.startswith('if '):
                condition = re.sub(r'^if\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'  # Додаємо умову без ключового слова if
            elif line.startswith('elif '):
                condition = re.sub(r'^elif\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'  # Додаємо умову без elif
            elif line.startswith('else'):
                pseudocode += ''  # else пропускаємо або можемо написати "інакше", якщо потрібно

            # Обробка циклів for
            elif line.startswith('for '):
                match = re.match(
                    r'for\s+(\w+)\s+in\s+range\(\s*(.+?)\s*,\s*(.+?)\s*\):', line)
                if match:
                    var, start, end = match.groups()
                    # Перетворюємо цикл for у вираз з умовою (наприклад: i <= n)
                    pseudocode += f'{var} <= {end}\n'
                else:
                    pseudocode += line.rstrip(':') + '\n'  # Якщо формат інший — залишаємо як є

            # Обробка циклів while
            elif line.startswith('while '):
                condition = re.sub(r'^while\s+(.*):$', r'\1', line)
                pseudocode += f'{condition}\n'  # Додаємо тільки умову

            # Обробка оголошень функцій
            elif line.startswith('def '):
                func_name = re.sub(r'^def\s+(\w+)\s*\(.*\):$', r'\1', line)
                pseudocode += f'function {func_name}\n'  # Замість "def" пишемо "function"

            else:
                # Усі інші рядки додаємо без змін
                pseudocode += line + '\n'

        print(pseudocode)  # Виводимо псевдокод у консоль (можна прибрати для фінальної версії)
        return pseudocode  # Повертаємо результат
