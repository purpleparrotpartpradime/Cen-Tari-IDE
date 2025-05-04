# IDE rules for Cen-Tari
# cen_tari_translator.py

"""
Cen-Tari → Python translator

Supports:
  • HTML-like tags:  <div id="foo">{ ... } → DOM creation via js.document
  • Java/C# style:  class, interface, functions, var declarations, types
  • Control flow:   if/else/elif, switch, for, foreach, while
  • Exception:      try/catch/finally
  • Operators:      &&→and, ||→or, !→not, ==, !=, ===, !==
  • Data:           arrays, maps, strings, numbers, booleans, null
  • Charts:         chart(type, data) → matplotlib/plotly stub
  • 2D/3D games:    spawn(entity, x,y) etc. → placeholder calls
"""

import re
from textwrap import indent

# helper to escape quotes in HTML snippet
def _escape_html(s):
    return s.replace("'", "\\'").replace("\n", "\\n")

def patch(code: str) -> str:
    """Auto–patch: balance braces, semicolons on statements, close HTML blocks."""
    braces = 0
    lines = []
    for raw in code.splitlines():
        line = raw.rstrip()
        braces += line.count('{') - line.count('}')
        if line and not re.search(r'[;{\}]$', line):
            line += ';'
        lines.append(line)
    # append closing braces if unbalanced
    lines += ['}'] * braces
    return "\n".join(lines)

def translate(code: str, variables: dict = None) -> str:
    """
    Main translator entrypoint.
    Returns Python code string.
    """
    if variables is None:
        variables = {}

    py_lines = []
    indent_level = 0

    # preamble: import JS DOM helpers if HTML tags are used
    use_dom = '<' in code
    if use_dom:
        py_lines.append("from js import document")

    # inject user variables
    for name, val in variables.items():
        py_lines.append(f"{name} = {val!r}")
    if variables:
        py_lines.append("")  # blank line

    # regex patterns
    patterns = [
        # comments: // → #, /*…*/ → triple-quote
        (r'//(.*)', lambda m: f"# {m.group(1)}"),
        (r'/\*(.*?)\*/', lambda m: f'"""{m.group(1).strip()}"""'),
        # boolean & null
        (r'\btrue\b', 'True'),
        (r'\bfalse\b', 'False'),
        (r'\bnull\b', 'None'),
        # logical operators
        (r'&&', 'and'),
        (r'\|\|', 'or'),
        (r'!', 'not '),
        # equality
        (r'===', '=='),
        (r'!==', '!='),
    ]

    def apply_patterns(line):
        for pat, repl in patterns:
            line = re.sub(pat, repl, line)
        return line

    # split into tokens by brace to handle indent
    tokens = re.split(r'(\{|\})', code)
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue

        # opening brace → indent block
        if tok == '{':
            indent_level += 1
            continue
        # closing brace → dedent
        if tok == '}':
            indent_level = max(0, indent_level - 1)
            continue

        # apply basic pattern rewrites
        line = apply_patterns(tok)

        # variable declarations: var or types
        line = re.sub(r'\b(var|int|float|string|bool)\s+', '', line)
        # semicolon stripping
        if line.endswith(';'):
            line = line[:-1]

        # class/interface
        m = re.match(r'(public\s+)?class\s+(\w+)', line)
        if m:
            py = f"class {m.group(2)}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue
        m = re.match(r'(public\s+)?interface\s+(\w+)', line)
        if m:
            py = f"class {m.group(2)}:  # interface stub"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue

        # function definitions
        m = re.match(r'(public\s+)?(static\s+)?function\s+(\w+)\((.*?)\)', line)
        if m:
            name, args = m.group(3), m.group(4)
            py = f"def {name}({args}):"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue

        # if / else if / else
        m = re.match(r'if\s*\((.*)\)', line)
        if m:
            py = f"if {m.group(1)}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue
        m = re.match(r'else if\s*\((.*)\)', line)
        if m:
            indent_level = max(0, indent_level-1)
            py = f"elif {m.group(1)}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue
        if line.startswith('else'):
            indent_level = max(0, indent_level-1)
            py = "else:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue

        # switch → chained if/elif
        if line.startswith('switch'):
            # simplistic: switch(x) { → _switch = x
            m = re.match(r'switch\s*\((.*)\)', line)
            py_lines.append("    "*indent_level + f"_switch = {m.group(1)}")
            continue
        m = re.match(r'case\s+(.*):', line)
        if m:
            py = f"if _switch == {m.group(1)}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue
        if line.startswith('default:'):
            indent_level = max(0, indent_level-1)
            py = "else:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue

        # loops
        m = re.match(r'for\s*\(\s*(.*?);\s*(.*?);\s*(.*?)\)', line)
        if m:
            init, cond, incr = m.groups()
            # translate init
            py_init = apply_patterns(init).rstrip(';')
            py_cond = apply_patterns(cond)
            py_incr = apply_patterns(incr).rstrip(';')
            py = f"{py_init}\n{'    '*indent_level}while {py_cond}:\n{'    '*(indent_level+1)}# loop body\n{'    '*(indent_level+1)}{py_incr}"
            py_lines.append("    "*indent_level + py)
            continue
        m = re.match(r'foreach\s*\(\s*(\w+)\s+in\s+(.*)\)', line)
        if m:
            var, col = m.groups()
            py = f"for {var} in {col}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue
        m = re.match(r'while\s*\((.*)\)', line)
        if m:
            py = f"while {m.group(1)}:"
            py_lines.append("    "*indent_level + py)
            indent_level += 1
            continue

        # try/catch/finally
        if line.startswith('try'):
            py_lines.append("    "*indent_level + "try:")
            indent_level += 1
            continue
        m = re.match(r'catch\s*\(\s*(\w+)\s*\)', line)
        if m:
            indent_level = max(0, indent_level-1)
            py_lines.append("    "*indent_level + f"except Exception as {m.group(1)}:")
            indent_level += 1
            continue
        if line.startswith('finally'):
            indent_level = max(0, indent_level-1)
            py_lines.append("    "*indent_level + "finally:")
            indent_level += 1
            continue

        # HTML tag block: <tag attr="...">{ ... }
        m = re.match(r'<(\w+)(.*?)>', tok)
        if m:
            tag, attrs = m.groups()
            attr_str = attrs.strip()
            # build element
            var = f"el_{indent_level}_{tag}"
            py_lines.append("    "*indent_level +
                f"{var} = document.createElement('{tag}')")
            # parse attributes
            for attr_m in re.finditer(r'(\w+)\s*=\s*\"(.*?)\"', attr_str):
                a, v = attr_m.groups()
                py_lines.append("    "*indent_level +
                    f"{var}.setAttribute('{a}','{v}')")
            # append to parent (or body if top)
            parent = f"el_{indent_level-1}_root" if indent_level>0 else "document.body"
            py_lines.append("    "*indent_level +
                f"{parent}.appendChild({var})")
            indent_level += 1
            continue

        # closing HTML (</tag>) just dedents
        if re.match(r'</\w+>', tok):
            indent_level = max(0, indent_level-1)
            continue

        # chart primitive
        m = re.match(r'chart\s*\(\s*(\w+)\s*,\s*(.*?)\s*\)', line)
        if m:
            t, d = m.groups()
            py = f"draw_chart('{t}', {d})  # implement in runtime"
            py_lines.append("    "*indent_level + py)
            continue

        # game primitive
        m = re.match(r'spawn\s*\(\s*(\w+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', line)
        if m:
            ent, x, y = m.groups()
            py = f"spawn('{ent}', {x}, {y})"
            py_lines.append("    "*indent_level + py)
            continue

        # fallback: raw Python–style call or assignment
        py_lines.append("    "*indent_level + line)

    # if nothing produced, ensure at least pass
    if not py_lines:
        return "pass"
    return "\n".join(py_lines)
