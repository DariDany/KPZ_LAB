import re
from PyChart import Preprocessor


class PyPreprocessor(Preprocessor):

    def _parse(self) -> None:
        # Розбиваємо вхідний файл пострічково
        for i in self._file:
            # Видаляємо однорядкові коментарі
            i = re.sub(r'\#.*', '', i)
            striped_i = i.strip()

            # Ігноруємо порожні рядки
            if striped_i != '\n' and striped_i != '':
                # Обробка випадку, коли конструкція керування не закінчується двокрапкою
                if self._is_control_structure(i) and striped_i[-1] != ':':
                    body = striped_i.split(':')[-1]
                    # Додаємо заголовок конструкції до результату
                    self._parsed_code.append(i.replace(body, ''))
                    # Формуємо тіло з відповідним рівнем відступів
                    body = self._set_level_of_line(body, self._get_level_of_line(i)+1)
                    self._parsed_code.append(body)
                else:
                    # Додаємо звичайний рядок до обробленого коду
                    self._parsed_code.append(i)

    def _get_serealized_code(self, code: list) -> list:
        # Перетворює список коду у вкладену структуру з блоками коду (словниками)
        levels = []
        i = 0

        while i < len(code):
            item = code[i]

            # Якщо рядок — це керуюча конструкція, обробляємо як блок
            if self._is_control_structure(item):
                end = self._find_end_of_body(code, i)
                # Рекурсивно обробляємо тіло блоку
                levels.append({item.strip(): self._get_serealized_code(code[i+1:end+1])})
                i = end
            else:
                # Звичайний рядок — додаємо до результату
                levels.append(item.strip())

            i += 1

        return levels

    def _cut_functions(self, serealized_code: list):
        # Витягує функції з серіалізованого коду, видаляючи їх із основного тіла
        functions = []
        new_code = []

        for line in serealized_code:
            if isinstance(line, dict) and len(line) == 1:
                key = next(iter(line))
                value = line[key]

                # Якщо знайдена функція
                if 'def' in key:
                    inner_functions = self._cut_functions(value)
                    value.append("End")  # Позначення кінця функції
                    functions.append({key: value})
                    functions.extend(inner_functions)
                else:
                    new_code.append(line)
            else:
                new_code.append(line)

        # Оновлюємо основний код без функцій
        serealized_code.clear()
        serealized_code.extend(new_code)

        return functions

    def _find_end_of_body(self, code: list, position: int) -> int:
        # Знаходить останній рядок блоку з однаковим або більшим відступом
        last_level = self._get_level_of_line(code[position])
        end = position

        for i in code[position+1::]:
            if self._get_level_of_line(i) > last_level:
                end += 1
            else:
                break

        return end

    @staticmethod
    def _get_level_of_line(line) -> int:
        # Підраховує рівень відступу (кількість табуляцій у вигляді пробілів)
        return line.count('    ')

    @staticmethod
    def _increase_level_of_line(line, increase) -> str:
        # Збільшує рівень відступу у рядку
        level = PyPreprocessor._get_level_of_line(line)
        return line.replace('    ' * level, '    ' * (level+increase))

    @staticmethod
    def _set_level_of_line(line, level) -> str:
        # Встановлює чіткий рівень відступу у рядку
        line = line.strip()
        return '    ' * level + line

    def _find_all_veribles(self, code=None) -> list:
        if code is None:
            code = []

        if not code:
            code = self._parsed_code
        m = []

        # Пошук усіх змінних у коді
        for string in code:
            if type(string) == str:
                try:
                    # Знаходимо всі можливі оголошення та використання змінних
                    m += re.findall(r'(\w+)\.? ?= ?', string)
                    m += re.findall(r'for (\w+)\.?', string)
                    m += re.findall(r'while (\w+)\.?', string)
                    m += re.findall(r'for (\w+)', string)
                    m += re.findall(r'in +(\w+)\.?', string)
                    if '(' in string:
                        # Отримуємо змінні з аргументів функцій
                        m += re.findall(r'[a-zA-Z_0-9]+',
                                        string[string.index('(') + 1:string[::-1].index(')')])
                except ValueError:
                    print('wrong syntax on line:', f'"{string}"')
            else:
                # Рекурсивний пошук у вкладених блоках
                value = list(string.values())[0]
                m += self._find_all_veribles(value)

        m = list(set(m))  # Унікальні значення

        # Видаляємо ключові слова Python
        special_words = ['True', 'False', 'and',
                         'len', 'input', 'print', 'int', 'range']
        for sw in special_words:
            if sw in m:
                m.remove(sw)

        # Видаляємо числові значення
        new_m = []
        for e in m:
            if not e.isdigit():
                new_m.append(e)
        m = new_m

        return m

    def _get_function_name(self, line: str) -> str:
        # Видаляємо ключове слово 'def' та дужки, залишаємо тільки ім'я функції
        line = re.sub(r'def |\:', '', line)
        output = ''
        for i in line:
            if i != '(':
                output += i
            else:
                break

        return output

    def _get_fun_args(self, line: str, fun_name='') -> list:
        # Витягуємо список аргументів функції за її заголовком
        line = line[line.index(f'{fun_name}(')+len(fun_name) + 1:line.index(')')] + ','
        args = []
        last_arg = ''
        for i in line:
            if i == ',' and len(last_arg) > 0:
                last_arg = last_arg.strip()
                # Перевірка на правильне закриття дужок
                if (last_arg.count('[') + last_arg.count(']')) % 2 == 0 and (last_arg.count('{') + last_arg.count('}')) % 2 == 0:
                    args.append(last_arg)
                    last_arg = ''
                else:
                    last_arg += i
            else:
                last_arg += i
        return args

    @staticmethod
    def _is_control_structure(line: str) -> bool:
        # Перевіряє, чи є рядок керуючою конструкцією (if, for, def тощо)
        line = line.strip()
        return line[0:2] == 'if' or line[0:4] == 'elif' or line[0:3] == 'for' or line[0:5] == 'while' or line[0:4] == 'else' or line[0:4] == 'def '
