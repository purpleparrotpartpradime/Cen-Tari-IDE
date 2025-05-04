# cen_tari_runtime.py
import builtins
from js import console, document

def execute_cen_tari(python_code: str, show_ui: bool=True, log_fn=None):
    def _print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        if log_fn:
            log_fn(msg)
        else:
            console.log(msg)
    builtins.print = _print
    env = {}
    try:
        exec(python_code, env, env)
    except Exception as e:
        err = f"Runtime error: {e}"
        if log_fn:
            log_fn(err)
        else:
            console.error(err)
