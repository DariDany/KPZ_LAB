from graphviz import Digraph
import json

with open("example.py.json", "r") as f:
    data = json.load(f)


def json_to_flowchart(json_data, output_file="flowchart"):
    dot = Digraph(format="png")

    for block in json_data["blocks"]:
        dot.node(block["cur_el_id"], block["text"], shape="box")

    for arrow in json_data["arrows"]:
        dot.edge(
            json_data["blocks"][arrow["startIndex"]]["cur_el_id"],
            json_data["blocks"][arrow["endIndex"]]["cur_el_id"]
        )

    dot.render(output_file)
    print(f"Блок-схема збережена як {output_file}.png")


json_to_flowchart(data)
