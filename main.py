# main.py
from cen_tari_translator import translate
from cen_tari_runtime import execute_cen_tari
from cen_tari_packager import make_exe
from js import alert, console, window

# State
_logging_enabled = True
_last_translated = ""
_variables = {}

def _log(msg: str):
    if _logging_enabled:
        console.log(msg)
        # Also mirror into our on-page log div
        log_div = window.document.getElementById("output-log")
        entry = window.document.createElement("div")
        entry.textContent = msg
        log_div.appendChild(entry)

def run_all():
    """Translate + execute in UI + log all."""
    global _last_translated
    code = window.document.getElementById("code-editor").value
    _log("Translating Cen-Tari → Python…")
    python_code = translate(code, variables=_variables)
    _last_translated = python_code
    _log(python_code)
    _log("Executing…")
    execute_cen_tari(python_code, show_ui=True, log_fn=_log)

def execute_only():
    """Translate + execute only in terminal (no UI)."""
    global _last_translated
    code = window.document.getElementById("code-editor").value
    _log("Translating Cen-Tari → Python…")
    python_code = translate(code, variables=_variables)
    _last_translated = python_code
    _log(python_code)
    _log("Executing (logs only)…")
    execute_cen_tari(python_code, show_ui=False, log_fn=_log)

def patch_code():
    """Attempt to auto-correct syntax errors."""
    code = window.document.getElementById("code-editor").value
    _log("Patching code…")
    fixed = translate.patch(code)
    window.document.getElementById("code-editor").value = fixed
    _log("Patch applied.")

def build_html_app():
    """Generate a standalone HTML file that runs the Cen-Tari code."""
    code = window.document.getElementById("code-editor").value
    html = f"""<!DOCTYPE html>
<html><head>
  <meta charset="utf-8">
  <title>Cen-Tari App</title>
  <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css">
  <script defer src="https://pyscript.net/latest/pyscript.js"></script>
</head><body>
<py-script>
from cen_tari_translator import translate
from cen_tari_runtime import execute_cen_tari
cen_code = {code!r}
py_code = translate(cen_code, variables={})
execute_cen_tari(py_code, show_ui=True)
</py-script>
</body></html>"""
    blob = window.Blob.new([html], { "type": "text/html" })
    url = window.URL.createObjectURL(blob)
    window.open(url, "_blank")
    _log("HTML app built and opened in new window.")

def toggle_logging():
    """Turn logging on/off."""
    global _logging_enabled
    _logging_enabled = not _logging_enabled
    state = "ON" if _logging_enabled else "OFF"
    alert(f"Logging is now {state}")

def prompt_variable():
    """Ask user to set or change a variable."""
    name = window.prompt("Variable name:")
    if not name:
        return
    val = window.prompt(f"Set value for '{name}' (number, true/false):")
    try:
        if val.lower() in ("true","false"):
            _variables[name] = val.lower() == "true"
        else:
            _variables[name] = float(val)
        _log(f"Variable '{name}' set to {_variables[name]}")
    except Exception:
        alert("Invalid value; must be number or true/false.")

def package_exe():
    """Package current code + runtime into a standalone exe."""
    if not _last_translated:
        alert("You must Run at least once before packaging.")
        return
    _log("Packaging into .exe…")
    success, msg = make_exe(_last_translated, variables=_variables)
    if success:
        alert("EXE built successfully:\n" + msg)
    else:
        alert("Packaging failed:\n" + msg)
