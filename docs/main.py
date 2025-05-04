# main.py

import os
from dotenv import load_dotenv
from cen_tari_translator import translate
from cen_tari_runtime    import execute_cen_tari
from cen_tari_packager   import make_exe

from pyodide      import create_proxy
from js           import document, console, alert, window

# Load PAT from .env file
load_dotenv()
GITHUB_PAT = os.getenv('GITHUB_PAT')

_logging_enabled = True
_last_translated = ""
_variables = {}

def _log(msg: str):
    if _logging_enabled:
        console.log(msg)
        log_div = document.getElementById("output-log")
        entry   = document.createElement("div")
        entry.textContent = msg
        log_div.appendChild(entry)

def run_all(*args):
    global _last_translated
    code = document.getElementById("code-editor").value
    _log("▶ Translating Cen-Tari → Python…")
    py_code = translate(code, variables=_variables)
    _last_translated = py_code
    _log(py_code)
    _log("▶ Executing (with UI)…")
    execute_cen_tari(py_code, show_ui=True, log_fn=_log)

def execute_only(*args):
    global _last_translated
    code = document.getElementById("code-editor").value
    _log("▶ Translating Cen-Tari → Python…")
    py_code = translate(code, variables=_variables)
    _last_translated = py_code
    _log(py_code)
    _log("▶ Executing (logs only)…")
    execute_cen_tari(py_code, show_ui=False, log_fn=_log)

def patch_code(*args):
    code = document.getElementById("code-editor").value
    _log("🔧 Patching code…")
    fixed = translate.patch(code)
    document.getElementById("code-editor").value = fixed
    _log("✅ Patch applied.")

def build_html_app(*args):
    code = document.getElementById("code-editor").value
    html = f"""<!DOCTYPE html>
<html><head>
  <meta charset="utf-8">
  <title>Cen-Tari App</title>
  <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css">
  <script defer src="https://pyscript.net/latest/pyscript.js"></script>
</head><body>
<py-script>
from cen_tari_translator import translate
from cen_tari_runtime    import execute_cen_tari
cen_code = {code!r}
py_code  = translate(cen_code, variables={})
execute_cen_tari(py_code, show_ui=True)
</py-script>
</body></html>"""
    blob = window.Blob.new([html], {{ "type": "text/html" }})
    url  = window.URL.createObjectURL(blob)
    window.open(url, "_blank")
    _log("📦 HTML app built & opened.")

def toggle_logging(*args):
    global _logging_enabled
    _logging_enabled = not _logging_enabled
    state = "ON" if _logging_enabled else "OFF"
    alert(f"Logging is now {state}")

def prompt_variable(*args):
    name = window.prompt("Variable name:")
    if not name:
        return
    val = window.prompt(f"Set value for '{{name}}' (number or true/false):")
    try:
        if val.lower() in ("true","false"):
            _variables[name] = val.lower() == "true"
        else:
            _variables[name] = float(val)
        _log(f"Variable '{{name}}' = {{_variables[name]}}")
    except Exception:
        alert("❌ Invalid value; must be a number or true/false.")

def package_exe(*args):
    if not _last_translated:
        alert("⚠️ Run at least once before packaging.")
        return
    _log("📦 Packaging into EXE…")
    success, msg = make_exe(_last_translated, variables=_variables)
    if success:
        alert("✅ EXE built:\n" + msg)
    else:
        alert("❌ Packaging failed:\n" + msg)

def _bind_buttons():
    mapping = {
      "btn-run":     run_all,
      "btn-execute": execute_only,
      "btn-patch":   patch_code,
      "btn-build":   build_html_app,
      "btn-log":     toggle_logging,
      "btn-variable":prompt_variable,
      "btn-package": package_exe
    }
    for btn_id, func in mapping.items():
        btn = document.getElementById(btn_id)
        if btn is None:
            console.warn(f"[Cen-Tari IDE] Missing element: {btn_id}")
            continue
        btn.addEventListener("click", create_proxy(lambda ev, f=func: f()))
    console.log("[Cen-Tari IDE] Buttons bound successfully.")

_bind_buttons()
