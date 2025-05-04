# cen_tari_translator.py
import re
from textwrap import indent

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
    use_dom = '<' in code
    if use_dom:
        py_lines.append("from js import document")
    for name, val in variables.items():
        py_lines.append(f"{name} = {val!r}")
    if variables:
        py_lines.append("")
    patterns = [
        (r'//(.*)', lambda m: f"# {m.group(1)}"),
        (r'/\*(.*?)\*/', lambda m: f'"""{m.group(1).strip()}"""'),
        (r'\btrue\b', 'True'),
        (r'\bfalse\b', 'False'),
        (r'\bnull\b', 'None'),
        (r'&&', 'and'),
        (r'\|\|', 'or'),
        (r'!', 'not '),
        (r'===', '=='),
        (r'!==', '!=')
    ]
    def apply_patterns(line):
        for pat, repl in patterns:
            line = re.sub(pat, repl, line)
        return line
    tokens = re.split(r'(\{|\})', code)
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        if tok == '{':
            indent_level += 1
            continue
        if tok == '}':
            indent_level = max(0, indent_level-1)
            continue
        line = apply_patterns(tok)
        line = re.sub(r'\b(var|int|float|string|bool)\s+', '', line)
        if line.endswith(';'):
            line = line[:-1]
        py_lines.append("    "*indent_level + line)
    if not py_lines:
        return "pass"
    return "\n".join(py_lines)
