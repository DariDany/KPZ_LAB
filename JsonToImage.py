from graphviz import Digraph
import json
import os
import sys

# Перевірка: чи передано шлях до JSON-файлу через аргументи командного рядка
if len(sys.argv) < 2:
    print("Потрібен шлях до JSON-файлу.")
    sys.exit(1)

# Отримуємо шлях до JSON-файлу з аргументів командного рядка
json_path = sys.argv[1]

# Видаляємо розширення .json з імені файлу
output_name = os.path.splitext(json_path)[0]

with open(json_path, "r", encoding='utf-8') as f:
    data = json.load(f)


def json_to_flowchart(json_data, output_file="flowchart"):
    """
    Побудова блок-схеми на основі структури з JSON-файлу.

    Args:
        json_data (dict): Дані блоків та стрілок у форматі JSON.
        output_file (str): Назва вихідного файлу (без розширення).
    """
    dot = Digraph(format="png")  # Створюємо об'єкт графу у форматі PNG

    # Додаємо всі блоки до графу
    for block in json_data["blocks"]:
        dot.node(block["cur_el_id"], block["text"], shape=block["shape"])

    # Додаємо стрілки між блоками
    for arrow in json_data["arrows"]:
        label = arrow.get("label", "")
        # Додаємо стрілку від початкового до кінцевого блоку
        dot.edge(
            json_data["blocks"][arrow["startIndex"]]["cur_el_id"],
            json_data["blocks"][arrow["endIndex"]]["cur_el_id"],
            label=label  # Додаємо мітку до стрілки
        )

    if os.path.exists(output_file + ".png"):
        os.remove(output_file + ".png")

    dot.render(output_file, cleanup=True)
    print(f"Блок-схема збережена як {output_file}.png")


json_to_flowchart(data, output_file=os.path.splitext(json_path)[0])
