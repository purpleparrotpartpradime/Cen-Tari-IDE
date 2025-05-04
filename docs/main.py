# main.py

from cen_tari_translator import translate
from cen_tari_runtime import execute_cen_tari
from cen_tari_packager import make_exe
from pyodide import create_proxy
from js import document, console, alert, window

_logging = True
_vars = {}
_last_py = ""

def _log(msg):
    if _logging:
        console.log(msg)
        div = document.getElementById('output-log')
        e = document.createElement('div')
        e.textContent = msg
        div.appendChild(e)

def run_all(*e):
    global _last_py
    code = document.getElementById('code-editor').value
    _log('Translating...')
    py = translate(code, variables=_vars)
    _last_py = py
    _log(py)
    _log('Executing with UI...')
    execute_cen_tari(py, show_ui=True, log_fn=_log)

def execute_only(*e):
    global _last_py
    code = document.getElementById('code-editor').value
    _log('Translating...')
    py = translate(code, variables=_vars)
    _last_py = py
    _log(py)
    _log('Executing logs only...')
    execute_cen_tari(py, show_ui=False, log_fn=_log)

def patch_code(*e):
    code = document.getElementById('code-editor').value
    _log('Patching...')
    fixed = translate.patch(code)
    document.getElementById('code-editor').value = fixed
    _log('Patched.')

def build_html(*e):
    code = document.getElementById('code-editor').value
    html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>Cen-Tari App</title>
<link rel='stylesheet' href='https://pyscript.net/latest/pyscript.css'>
<script defer src='https://pyscript.net/latest/pyscript.js'></script>
</head><body>
<py-script>
from cen_tari_translator import translate
from cen_tari_runtime import execute_cen_tari
code = {code!r}
py = translate(code, variables={})
execute_cen_tari(py, show_ui=True)
</py-script>
</body></html>"""
    blob = window.Blob.new([html], {"type":"text/html"})
    url = window.URL.createObjectURL(blob)
    window.open(url)
    _log('Built HTML App.')

def toggle_log(*e):
    global _logging
    _logging = not _logging
    alert(f'Logging {"ON" if _logging else "OFF"}')

def prompt_var(*e):
    name = window.prompt('Var name:')
    if not name: return
    val = window.prompt('Value (number or true/false):')
    try:
        if val.lower() in ('true','false'):
            _vars[name] = val.lower()=='true'
        else:
            _vars[name] = float(val)
        _log(f'Var {name}={_vars[name]}')
    except:
        alert('Invalid.')

def package_exe(*e):
    if not _last_py:
        alert('Run first.')
        return
    _log('Packaging...')
    ok, msg = make_exe(_last_py, variables=_vars)
    if ok:
        alert('Built: '+msg)
    else:
        alert('Error: '+msg)

def bind():
    buttons = {
        'btn-run': run_all,
        'btn-execute': execute_only,
        'btn-patch': patch_code,
        'btn-build': build_html,
        'btn-log': toggle_log,
        'btn-variable': prompt_var,
        'btn-package': package_exe
    }
    for id, fn in buttons.items():
        el = document.getElementById(id)
        if el:
            el.addEventListener('click', create_proxy(lambda e, f=fn: f()))
    console.log('Buttons bound.')

bind()
