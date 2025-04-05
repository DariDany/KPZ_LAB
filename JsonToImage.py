from graphviz import Digraph
import json
import os
import sys

# Получаем путь к JSON-файлу из аргументов
if len(sys.argv) < 2:
    print("Потрібен шлях до JSON-файлу.")
    sys.exit(1)

json_path = sys.argv[1]
output_name = os.path.splitext(json_path)[0]  # example.py.json → example.py

with open(json_path, "r", encoding='utf-8') as f:
    data = json.load(f)


def json_to_flowchart(json_data, output_file="flowchart"):
    dot = Digraph(format="png")

    for block in json_data["blocks"]:
        dot.node(block["cur_el_id"], block["text"], shape=block["shape"])

    for arrow in json_data["arrows"]:
        dot.edge(
            json_data["blocks"][arrow["startIndex"]]["cur_el_id"],
            json_data["blocks"][arrow["endIndex"]]["cur_el_id"]
        )

    if os.path.exists(output_file + ".png"):
        os.remove(output_file + ".png")

    dot.render(output_file, cleanup=True)
    print(f"Блок-схема збережена як {output_file}.png")


json_to_flowchart(data, output_file=os.path.splitext(json_path)[0])
