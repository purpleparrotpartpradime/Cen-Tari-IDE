# cen_tari_translator.py
import re

def patch(code: str) -> str:
    """Simple auto-patch: ensure semicolons, balanced braces."""
    # (This is just a stub. Expand with real error-fixing!)
    lines = code.splitlines()
    patched = []
    for line in lines:
        line = line.rstrip()
        if line and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}'):
            line += ';'
        patched.append(line)
    return "\n".join(patched)

def translate(code: str, variables: dict = None) -> str:
    """
    Convert Cen-Tari to Python.
    - var x = 5;     → x = 5
    - if (...) {     → if ...:
    - }               → dedent
    - ;               → (line end)
    - true/false      → True/False
    """
    if variables is None:
        variables = {}

    out_lines = []
    indent = 0
    for raw in code.splitlines():
        line = raw.strip()
        # skip empty
        if not line:
            continue
        # var declarations
        line = re.sub(r'\bvar\s+', '', line)
        # replace boolean literals
        line = line.replace('true', 'True').replace('false', 'False')
        # if / while with braces
        m = re.match(r'(if|while)\s*\((.*)\)\s*\{', line)
        if m:
            cond = m.group(2)
            py = f"{m.group(1)} {cond}:"
            out_lines.append("    "*indent + py)
            indent += 1
            continue
        # closing brace
        if line == '}':
            indent = max(0, indent-1)
            continue
        # strip semicolon
        if line.endswith(';'):
            line = line[:-1]
        # standard line
        out_lines.append("    "*indent + line)
    # inject variables
    pre = []
    for name, val in variables.items():
        pre.append(f"{name} = {val!r}")
    return "\n".join(pre + out_lines)
