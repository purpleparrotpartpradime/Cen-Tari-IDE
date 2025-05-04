# cen_tari_runtime.py
import builtins
from pyodide import create_proxy
from js import console, document

def execute_cen_tari(python_code: str, show_ui: bool = True, log_fn=None):
    """
    Execute the translated Python code.
    If show_ui=True, any UI ops (e.g., DOM writes) are allowed.
    If False, we capture only print/log output.
    """
    # Redirect built-in print()
    def _print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        if log_fn:
            log_fn(msg)
        else:
            console.log(msg)
    builtins.print = _print

    # Exec environment
    env = {}
    try:
        exec(python_code, env, env)
    except Exception as e:
        err = f"Runtime error: {e}"
        if log_fn:
            log_fn(err)
        else:
            console.error(err)
