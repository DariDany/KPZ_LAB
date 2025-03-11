from PyChart import BlockDiagram


class Py2BlockDiagram(BlockDiagram):

    @staticmethod
    def _get_struct_type(line: str) -> str:
        line = line.strip()

        if line[0:2] == 'if':
            return 'if'
        elif line[0:4] == 'else':
            return 'else'
        elif line[0:4] == 'elif':
            return 'elif'
        elif line[0:3] == 'for':
            return 'loop'
        elif line[0:5] == 'while':
            return 'loop'
        elif line[0:4] == 'def ':
            return 'function'
        else:
            if 'print' in line:
                return 'output'
            else:
                return 'block'

    @staticmethod
    def _get_bd_type_of_line(line: str) -> str:
        line = line.strip()

        if line[0:2] == 'if':
            return "Condition"
        elif line[0:4] == 'else':
            return 'none'
        elif line[0:4] == 'elif':
            return "Condition"
        elif line[0:3] == 'for':
            return "Loop for"
        elif line[0:5] == 'while':
            return "Loop while"
        elif 'print' in line:
            return "Input / Output"
        elif 'return ' in line:
            return "Start / end"
        else:
            return "Block"
