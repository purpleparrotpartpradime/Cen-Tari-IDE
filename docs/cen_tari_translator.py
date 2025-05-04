# cen_tari_translator.py
import re
def patch(code: str) -> str:
    braces = 0
    lines = []
    for raw in code.splitlines():
        line = raw.rstrip()
        braces += line.count('{') - line.count('}')
        if line and not re.search(r'[;{]}$', line):
            line += ';'
        lines.append(line)
    lines += ['}'] * braces
    return "\n".join(lines)
def translate(code: str, variables: dict=None) -> str:
    if variables is None:
        variables = {}
    py_lines = []
    indent_level = 0
    if '<' in code:
        py_lines.append("from js import document")
    for n, v in variables.items():
        py_lines.append(f"{n} = {v!r}")
    if variables:
        py_lines.append("")
    for raw in code.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.endswith('{'):
            line = line[:-1] + ':'
            py_lines.append('    '*indent_level + line)
            indent_level += 1
            continue
        if line == '}':
            indent_level = max(0, indent_level-1)
            continue
        py_lines.append('    '*indent_level + line.rstrip(';'))
    return "\n".join(py_lines) or "pass"
