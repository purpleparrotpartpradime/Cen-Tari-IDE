# cen_tari_runtime.py
import builtins
from js import console,document
def execute_cen_tari(code,show_ui=True,log_fn=None):
    def p(*a):m=' '.join(str(x) for x in a);(log_fn or console.log)(m)
    builtins.print=p
    try:exec(code,{},{})
    except Exception as e:(log_fn or console.error)(f"Error:{e}")