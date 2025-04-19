import re
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict


class BlockDiagram(ABC):
    # Основний словник для зберігання діаграми
    _diagram = {
        "blocks": [],  # Блоки діаграми
        "arrows": [],  # Стрілки між блоками
        "x0": 0,  # Початкова координата X
        "y0": 100,  # Початкова координата Y
    }

    # Напрямки для стрілок
    _direction = {
        'UP': 0,  # Вгору
        'RIGHT': 1,  # Вправо
        'DOWN': 2,  # Вниз
        'LEFT': 3,  # Вліво
    }

    # Останні координати для розміщення блоків
    _last_x = 0
    _last_y = 0
    _last_if_id_list = []  # Стек ID для if-структур
    _last_arrow_pos_delta = 15  # Відступ для стрілок
    _blocks_indent = 150  # Відступ між блоками

    def __init__(self, pseudocode, code_tree: list, variables: list, base_coor=None, name='main',
                 start_block_index=0) -> None:
        # Ініціалізація діаграми
        if base_coor is None:
            base_coor = {'y': 0, 'x': 0}

        self._pseudocode = pseudocode  # Генератор псевдокоду
        self._last_x = base_coor['x']  # Початкова X координата
        self._last_y = base_coor['y']  # Початкова Y координата
        self._name = name  # Назва діаграми
        self._code_tree = self._connect_same_lines_in_tree(code_tree)  # Дерево коду
        self._variables = variables  # Змінні програми
        self._forbidden_aria = []  # Заборонені області для розміщення
        self._start_block_index = start_block_index  # Початковий індекс блоку

    def build(self) -> dict:
        # Побудова діаграми блоків
        name = self._name
        if name == 'main':
            name = ''

        # Додаємо стартовий блок
        self._diagram['blocks'].insert(0,
                                       self._form_block(f'Start {name}',
                                                        {'y': self._last_y - 100,
                                                         'x': self._last_x},
                                                        uuid.uuid1().hex,
                                                        '0',
                                                        'Start / end'))
        # Додаємо всі блоки з дерева коду
        self._diagram['blocks'] += self._add_blocks(self._code_tree)

        # Додаємо кінцевий блок для основної діаграми
        if self._name == 'main':
            self._diagram['blocks'].append(
                self._form_block('End',
                                 {'y': self._last_y + 100, 'x': self._last_x},
                                 uuid.uuid1().hex,
                                 '0',
                                 'Start / end'))

        # Налаштування індексів, вирівнювання та стрілок
        self._set_block_indexes()
        self._align_if_else_bodies()
        self._set_all_forbidden_areas()
        self._connect_all_blocks_by_arrows()

        return self._diagram

    @staticmethod
    def build_from_programs_list(programs: list, pseudocode, diagram_class):
        # Побудова діаграми зі списку програм
        y = 0
        last_index = 0
        super_diagram = {
            "blocks": [],
            "arrows": [],
            "x0": 0,
            "y0": 0,
        }

        # Обробка кожної програми зі списку
        for prog in programs:
            diagram = diagram_class(pseudocode, prog['code'], prog['variables'], {
                'y': y, 'x': 0}, prog['name'], last_index)
            diagram = diagram.build()

            # Оновлення індексів
            last_index = max([b['index'] for b in diagram['blocks']]) + 1

            # Додавання блоків та стрілок до супер-діаграми
            super_diagram['blocks'] += diagram['blocks']
            super_diagram['arrows'] += diagram['arrows']
            y += len(diagram['blocks']) * diagram_class._blocks_indent

            # Очищення діаграми для наступної ітерації
            diagram_class._diagram['blocks'] = []
            diagram_class._diagram['arrows'] = []

        return super_diagram

    def debug(self) -> dict:
        # Метод для налагодження
        self.build()
        return {'diagram': self._diagram, 'forb_area': self._forbidden_aria}

    def _form_block(self, text='', pos=None, cur_el_id='0', parent_id='0', block_type='none'):
        # Формування блоку діаграми
        if pos is None:
            pos = {'x': 0, 'y': 0}

        # Визначення типу блоку
        if block_type == 'none':
            block_type = self._get_bd_type_of_line(text.strip().split('\n')[0])

        text = text.strip()

        if not text:
            return None

        code = text
        struct_type = self._get_struct_type(code)
        size = BlockDiagram._get_size_of_block(text.split('\n'))

        # Визначення форми блоку
        shape = "rectangle"  # Прямокутник за замовчуванням
        if block_type == "Start / end":
            shape = "oval"  # Овал для початку/кінця
        elif block_type == "Input / Output":
            shape = "parallelogram"  # Паралелограм для вводу/виводу
        elif block_type == "Logical Operator":
            shape = "diamond"  # Ромб для логічних операторів

        # Конвертація коду в псевдокод
        text = self._to_pseudocode(text)

        if not text.strip():
            return None

        # Створення словника блоку
        block = {
            "code": code,
            "cur_el_id": cur_el_id,
            "parent_id": parent_id,
            "struct_type": struct_type,
            "x": pos['x'],
            "y": pos['y'],
            "text": text,
            "width": size['width'],
            "height": size['height'],
            "type": block_type,
            "shape": shape,
            "isMenuBlock": False,
            "fontSize": 14,
            "textHeight": 14,
            "isBold": False,
            "isItalic": False,
            "textAlign": "center",
            "labelsPosition": 1
        }

        return block

    @abstractmethod
    def _get_struct_type(line: str) -> str:
        """
        Визначає тип рядка коду.
        Наприклад: "if a > 4" => 'if'

        Аргументи:
            line: рядок коду

        Повертає:
            'if', 'else', 'elif', 'loop', 'function', 'output', 'block'
        """
        if line:
            return 'block'

    @staticmethod
    def _get_size_of_block(lines: list) -> dict:
        # Розрахунок розмірів блоку на основі кількості рядків
        height = len(lines) * 8
        width = 100

        for line in lines:
            if type(line) == str:
                line = line.strip()
                width = max(width, len(line) * 9)

        return {'width': max(100, width), 'height': max(height, 40)}

    def _is_point_free(self, position: dict) -> bool:
        # Перевірка, чи точка вільна для розміщення
        x = position['x']
        y = position['y']
        for pos in self._forbidden_aria:
            if not ((x < pos['x0'] or x > pos['x1']) or (y < pos['y0'] or y > pos['y1'])):
                return False
        return True

    def _is_path_free(self, position: dict, coor='y') -> bool:
        # Перевірка, чи шлях між точками вільний
        coor1 = position['start']
        coor2 = position['end']

        if coor2[coor] - coor1[coor] > 0:
            direction_coef = 1
        else:
            direction_coef = -1

        coor1[coor] += 25 * direction_coef
        begin = 0
        end = abs(coor2[coor] - coor1[coor])
        while begin <= end:
            if self._is_point_free(coor1):
                coor1[coor] += 1 * direction_coef
            elif coor1[coor] == coor2[coor]:
                return True
            else:
                return False

            begin += 1
        return True

    @abstractmethod
    def _get_bd_type_of_line(line: str) -> str:
        """
        Визначає тип рядка для блок-діаграми.

        Аргументи:
            line: рядок коду

        Повертає:
            'Умова', 'none', 'Цикл for', 'Ввід / вивід', 'Початок / кінець', 'Блок'
        """
        if line:
            return 'Блок'

    def _set_forbidden_aria(self, position: dict, size: dict) -> None:
        # Встановлення забороненої області навколо блоку
        x0 = position['x'] - size['width'] / 2
        x1 = position['x'] + size['width'] / 2
        y0 = position['y'] - size['height'] / 2
        y1 = position['y'] + size['height'] / 2
        self._forbidden_aria.append({'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1})

    def _set_all_forbidden_areas(self) -> None:
        # Встановлення заборонених областей для всіх блоків
        for block in self._diagram['blocks']:
            self._set_forbidden_aria({'x': block['x'], 'y': block['y']},
                                     {'width': block['width'], 'height': block['height']})

    def _add_blocks(self, code_tree: list, parent_id='0') -> list:
        # Додавання блоків з дерева коду
        blocks = []

        for code in code_tree:
            cur_el_id = uuid.uuid1().hex
            if type(code) == str:
                self._last_y += self._blocks_indent
                block = self._form_block(
                    code, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
                if block is not None:
                    blocks.append(block)
                else:
                    self._last_y -= self._blocks_indent
            else:
                self._last_y += self._blocks_indent
                key = list(code.keys())[0]
                value = list(code.values())[0]
                block = self._form_block(
                    key, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
                if 'if ' in key:
                    self._last_if_id_list.append(cur_el_id)

                elif 'else' == key.replace(':', '').strip():
                    self._last_y -= self._blocks_indent
                    blocks += self._add_blocks(value,
                                               self._last_if_id_list[-1] + '-else')
                    self._last_if_id_list.pop()
                elif 'for ' in key:
                    # Обробка циклу for
                    match = re.match(
                        r'for\s+(\w+)\s+in\s+range\(\s*(.+?)\s*,\s*(.+?)\s*\):', key)

                    if match:
                        loop_var = match.group(1)
                        increment_line = f'{loop_var} = {loop_var} + 1'
                        if increment_line not in value:
                            value.append(increment_line)

                    self._last_y += 50

                    if block is not None:
                        blocks.append(block)

                    blocks += self._add_blocks(value, cur_el_id)
                    continue

                elif 'while ' in key:
                    self._last_y += 50

                    if block is not None:
                        blocks.append(block)

                    blocks += self._add_blocks(value, cur_el_id)
                    continue
                else:
                    self._last_y -= self._blocks_indent
                    blocks += self._add_blocks(value,
                                               self._last_if_id_list[-1])
                if block is not None:
                    blocks.append(block)
                    blocks += self._add_blocks(value, cur_el_id)

        return blocks

    def _add_for_loop_block(self, body, parent_id):
        # Додавання блоків для циклу for
        blocks = []
        for line in body:
            cur_el_id = uuid.uuid1().hex
            self._last_y += self._blocks_indent
            block = self._form_block(
                line, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
            if block is not None:
                blocks.append(block)
            else:
                self._last_y -= self._blocks_indent

        return blocks

    def _add_while_loop_block(self, body, parent_id):
        # Додавання блоків для циклу while
        blocks = []
        for line in body:
            cur_el_id = uuid.uuid1().hex
            self._last_y += self._blocks_indent
            block = self._form_block(
                line, {'x': 0, 'y': self._last_y}, cur_el_id, parent_id)
            if block is not None:
                blocks.append(block)
            else:
                self._last_y -= self._blocks_indent
        return blocks

    def _connect_same_lines_in_tree(self, code_tree: list) -> list:
        # Об'єднання однакових рядків у дереві коду
        tree = []

        for item in code_tree:
            if isinstance(item, str):
                tree.append(item.strip())
            else:
                key = list(item.keys())[0]
                value = item[key]
                tree.append({key: self._connect_same_lines_in_tree(value)})

        return tree

    def _set_block_indexes(self) -> None:
        # Встановлення індексів для блоків
        count = self._start_block_index
        for block in self._diagram['blocks']:
            block['index'] = count
            count += 1

    def _to_pseudocode(self, lines: str) -> str:
        # Конвертація коду в псевдокод
        return self._pseudocode.to_pseudocode(lines)

    def _draw_arrow(self, start_end_pos: dict, start_end_indexes: dict, direction: dict, label: str = "") -> None:
        # Малювання стрілки між блоками
        dirs = self._direction
        delta = self._last_arrow_pos_delta - 1

        # Перевірка на наявність дублікатів стрілок
        for arrow in self._diagram['arrows']:
            if arrow['startIndex'] == start_end_indexes['start'] and \
                    arrow['endIndex'] == start_end_indexes['end'] and \
                    arrow.get('label', '') == label:
                return  # дубль — не додаємо вдруге

        arrow = {
            "startIndex": start_end_indexes['start'],
            "endIndex": start_end_indexes['end'],
            "startConnectorIndex": direction['start'],
            "endConnectorIndex": direction['end'],
            "nodes": [],
            "counts": [],
            "label": label
        }

        x1 = start_end_pos['start']['x']
        y1 = start_end_pos['start']['y']
        x2 = start_end_pos['end']['x']
        y2 = start_end_pos['end']['y']

        x_direction_coef = 1
        if direction['start'] == dirs['LEFT']:
            x_direction_coef = -1

        # Логіка малювання стрілок для різних напрямків
        if direction['start'] == dirs['LEFT'] and direction['end'] == dirs['RIGHT']:
            arrow['nodes'].append({'x': x1, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x2, 'y': y1}}, 'x'):
                y1 += 50

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}, 'y'):
                x1 += 50

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})
            arrow['nodes'].append({'x': x1 + delta, 'y': y2})
            arrow['nodes'].append({'x': x2, 'y': y2})

        elif direction['start'] == dirs['DOWN'] and direction['end'] == dirs['RIGHT']:
            arrow['nodes'].append({'x': x1, 'y': y1})
            y1 += 50
            arrow['nodes'].append({'x': x1, 'y': y1})

            while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}, 'y'):
                x1 += 50 * x_direction_coef

            arrow['nodes'].append({'x': x1 + delta, 'y': y1})
            arrow['nodes'].append({'x': x1 + delta, 'y': y2})
            arrow['nodes'].append({'x': x2, 'y': y2})

        else:
            arrow['nodes'].append({'x': x1, 'y': y1})
            if not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x2, 'y': y2}}):
                while not self._is_path_free({'start': {'x': x1, 'y': y1}, 'end': {'x': x1, 'y': y2}}):
                    x1 += 30 * x_direction_coef

                arrow['nodes'].append({'x': x1 + delta, 'y': y1})
                arrow['nodes'].append({'x': x1 + delta, 'y': y2 - 40})
                arrow['nodes'].append({'x': x2, 'y': y2 - 40})
                arrow['nodes'].append({'x': x2, 'y': y2 + 40})
            else:
                arrow['nodes'].append({'x': x2, 'y': y2})

        for _ in arrow['nodes']:
            arrow['counts'].append(1)
        self._last_arrow_pos_delta -= 1
        self._diagram['arrows'].append(arrow)

    def _connect_blocks(self, block1: dict, block2: dict, direction: dict, label: str = "") -> None:
        # З'єднання двох блоків стрілкою
        self._draw_arrow(
            {'start': {'y': block1['y'], 'x': block1['x']},
             'end': {'y': block2['y'], 'x': block2['x']}},
            {'start': block1['index'], 'end': block2['index']},
            direction,
            label  # Мітка для стрілки
        )

    def _align_if_else_bodies(self) -> None:
        # Вирівнювання блоків if-else
        if_structs = self._find_blocks_by_property('struct_type', 'if')

        for if_struct in if_structs:
            struct_id = if_struct['cur_el_id']

            if_body = self._find_blocks_by_property('parent_id', struct_id)
            elif_body = self._find_blocks_by_property(
                'parent_id', struct_id + '-elif')
            else_body = self._find_blocks_by_property(
                'parent_id', struct_id + '-else')
            max_width_if_body = max([i['width']
                                     for i in if_body]) if if_body else 0

            base_x = if_struct['x']

            # Вирівнювання блоків if
            for block in if_body:
                block['x'] = base_x + max_width_if_body

            base_y = if_body[0]['y'] if if_body else 0

            # Вирівнювання блоків elif
            for block in elif_body:
                block['x'] = base_x + max_width_if_body
                block['y'] = base_y
                base_y += 100

            # Вирівнювання блоків else
            for block in else_body:
                block['x'] = base_x - max_width_if_body
                block['y'] = base_y
                base_y += 100

    def _find_blocks_by_property(self, block_property: str, value, required_field='', block_list=None) -> list:
        # Пошук блоків за властивістю
        if block_list is None:
            block_list = []
        if not block_list:
            block_list = self._diagram['blocks']
        output = []

        for block in block_list:
            if block[block_property] == value:
                if required_field != '':
                    output.append(block[required_field])
                else:
                    output.append(block)

        return output

    def _connect_all_blocks_by_arrows(self, parent_id='0') -> None:
        # З'єднання всіх блоків стрілками
        blocks = self._find_blocks_by_property('parent_id', parent_id)
        dirs = self._direction
        i = 0

        while i < len(blocks):
            b_c = blocks[i]
            b_n = blocks[i + 1] if i + 1 < len(blocks) else None
            struct_type = b_c['struct_type']
            cur_id = b_c['cur_el_id']

            if struct_type in ['block', 'output'] and b_n:
                self._connect_blocks(
                    b_c, b_n, {'start': dirs['DOWN'], 'end': dirs['UP']})

            elif struct_type == 'loop':
                # Обробка циклів
                body = self._find_blocks_by_property('parent_id', cur_id)
                if body:
                    # Стрелка "так" — в тіло циклу
                    self._connect_blocks(
                        b_c, body[0], {'start': dirs['DOWN'], 'end': dirs['UP']}, label="так"
                    )

                    # Рекурсивна обробка тіла циклу
                    self._connect_all_blocks_by_arrows(cur_id)

                    # Стрелка назад до умови циклу
                    self._connect_blocks(
                        body[-1], b_c, {'start': dirs['DOWN'],
                                        'end': dirs['UP']}
                    )

                # Стрелка "ні" — до наступного блоку
                if b_n:
                    self._connect_blocks(
                        b_c, b_n, {'start': dirs['RIGHT'], 'end': dirs['UP']}, label="ні"
                    )

            elif struct_type == 'if':
                # Обробка умовних конструкцій
                if_body = self._find_blocks_by_property('parent_id', cur_id)
                else_body = self._find_blocks_by_property(
                    'parent_id', cur_id + '-else')

                # Підключення "так" та "ні"
                if if_body:
                    self._connect_blocks(
                        b_c, if_body[0], {'start': dirs['RIGHT'], 'end': dirs['UP']}, label="так")
                    self._connect_all_blocks_by_arrows(cur_id)

                if else_body:
                    self._connect_blocks(
                        b_c, else_body[0], {'start': dirs['LEFT'], 'end': dirs['UP']}, label="ні")
                    self._connect_all_blocks_by_arrows(cur_id + '-else')

                # Підключення до наступного блоку після if-else
                continuation_block = b_n
                if continuation_block:
                    if if_body:
                        farthest = self._find_farthest_children([if_body[-1]])
                        for last in farthest:
                            self._connect_blocks(
                                last, continuation_block, {'start': dirs['DOWN'], 'end': dirs['UP']})
                    if else_body:
                        farthest = self._find_farthest_children(
                            [else_body[-1]])
                        for last in farthest:
                            self._connect_blocks(
                                last, continuation_block, {'start': dirs['DOWN'], 'end': dirs['UP']})
                    continuation_block['parent_id'] = cur_id

            i += 1

    def _find_farthest_children(self, blocks: list) -> list:
        # Пошук найвіддаленіших дочірніх блоків
        children = []
        if len(blocks) == 0:
            return []

        for block in blocks:
            struct_type = block['struct_type']
            body = self._find_blocks_by_property(
                'parent_id', block['cur_el_id'])
            else_body = self._find_blocks_by_property(
                'parent_id', block['cur_el_id'] + '-else')

            if struct_type == 'loop':
                if len(body) > 0:
                    children += self._find_farthest_children([body[-1]])
            elif struct_type == 'if':
                if len(body) > 0:
                    children += self._find_farthest_children([body[-1]])
                if len(else_body) > 0:
                    children += self._find_farthest_children([else_body[-1]])
                else:
                    children += [block]

            else:
                children.append(block)

        return children