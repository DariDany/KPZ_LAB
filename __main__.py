from PyPreprocessor import PyPreprocessor
from Py2BlockDiagram import Py2BlockDiagram
from Py2PseudoCode import Py2PseudoCode
import sys
import json
import subprocess


def main():
    args = sys.argv[1::]

    try:
        file_path = args[0]
        f = open(file_path, 'r', encoding='utf-8')
    except:
        try:
            file_path = input('path: ')
            f = open(file_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            exit('wrong path')

    p = PyPreprocessor(f)
    programs_list = p.get_programs_list()
    diagram = Py2BlockDiagram.build_from_programs_list(
        programs_list, Py2PseudoCode, Py2BlockDiagram)

    f.close()

    json_file_path = f'{file_path}.json'
    with open(json_file_path, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(diagram, indent=4))

    print(f'Diagram has been saved as {json_file_path}')

    # Виклик JsonToImage.py для створення блок-схеми
    try:
        subprocess.run([sys.executable, "JsonToImage.py",
                       json_file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Помилка при створенні блок-схеми: {e}")


if __name__ == "__main__":
    main()
