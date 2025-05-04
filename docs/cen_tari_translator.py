# cen_tari_translator.py
import re

def patch(code: str) -> str:
    lines, depth = [], 0
    for l in code.splitlines():
        ln = l.rstrip()
        depth += ln.count('{') - ln.count('}')
        if ln and not re.search(r'[;{}]$', ln):
            ln += ';'
        lines.append(ln)
    lines += ['}'] * depth
    return '\n'.join(lines)

def translate(code: str, variables: dict=None) -> str:
    if variables is None: variables={}
    out, indent = [], 0
    if '<' in code:
        out.append('from js import document')
    for k,v in variables.items():
        out.append(f"{k}={v!r}")
    for l in code.splitlines():
        ln = l.strip()
        if not ln: continue
        if ln.endswith('{'):
            out.append('    '*indent + ln[:-1] + ':')
            indent += 1
        elif ln == '}':
            indent = max(0, indent-1)
        else:
            out.append('    '*indent + ln.rstrip(';'))
    return '\n'.join(out) or 'pass'
