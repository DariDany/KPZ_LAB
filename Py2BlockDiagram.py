import re
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
        line = line.strip().lower()
        if line.startswith("for") or line.startswith("while"):
            return "Logical Operator"
        if line.startswith("if") or line.startswith("elif") or "?" in line:
            return "Logical Operator"  # Conditional operators
        elif line.startswith("for") or line.startswith("while"):
            return "Logical Operator"  # Loop conditions should also be diamonds
        elif any(keyword in line for keyword in ["input", "output", "print"]):
            return "Input / Output"  # Input/Output operations
        elif line.startswith("start") or line.startswith("end"):
            return "Start / end"  # Start/End points
        elif re.match(r"^[a-z_]\w*\s*=\s*[^=]", line):
            return "Block"
        return "Block"
