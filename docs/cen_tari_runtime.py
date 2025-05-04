# cen_tari_runtime.py
import builtins
from js import console, document

def execute_cen_tari(code: str, show_ui=True, log_fn=None):
    def _print(*args):
        msg = ' '.join(str(a) for a in args)
        if log_fn: log_fn(msg)
        else: console.log(msg)
    builtins.print = _print
    try:
        exec(code, {}, {})
    except Exception as e:
        err = f"Error: {e}"
        if log_fn: log_fn(err)
        else: console.error(err)
