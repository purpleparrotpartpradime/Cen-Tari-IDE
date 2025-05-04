# main.py
from cen_tari_translator import translate
from cen_tari_runtime import execute_cen_tari
from cen_tari_packager import make_exe
from pyodide import create_proxy
from js import document,console,alert,window
_logging=True;_vars={};_last_py=""
def _log(m): 
    if _logging:console.log(m);d=document.getElementById('output-log');e=document.createElement('div');e.textContent=m;d.appendChild(e)
def _clear():document.getElementById('output-view').innerHTML=''
def _render(fn):
    c=document.getElementById('output-view');orig=window.document.body;window.document.body=c;fn();window.document.body=orig
def run_all(*_):
    global _last_py;code=document.getElementById('code-editor').value;_clear();_log('Translating');py=translate(code,variables=_vars);_last_py=py;_log(py);_log('Exec UI');_render(lambda:execute_cen_tari(py,show_ui=True,log_fn=_log))
def execute_only(*_):
    global _last_py;code=document.getElementById('code-editor').value;_clear();_log('Translating');py=translate(code,variables=_vars);_last_py=py;_log(py);_log('Exec logs');execute_cen_tari(py,show_ui=False,log_fn=_log)
def patch(*_):code=document.getElementById('code-editor').value;_log('Patching');f=translate.patch(code);document.getElementById('code-editor').value=f;_log('Patched')
def build(*_):
    code=document.getElementById('code-editor').value;html=f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>Cen-Tari App</title><link rel='stylesheet' href='https://pyscript.net/latest/pyscript.css'><script defer src='https://pyscript.net/latest/pyscript.js'></script></head><body><py-script>from cen_tari_translator import translate;from cen_tari_runtime import execute_cen_tari;code={code!r};py=translate(code,variables={});execute_cen_tari(py,show_ui=True)</py-script></body></html>""";b=window.Blob.new([html],{'type':'text/html'});window.open(window.URL.createObjectURL(b));_log('Built App')
def toggle(*_):global _logging;_logging=not _logging;alert(f'Logging {"ON" if _logging else "OFF"}')
def varp(*_):n=window.prompt('Var name:');+''
def package(*_):_last_py or alert('Run first') or None;if _last_py:_log('Packaging');ok,msg=make_exe(_last_py,variables=_vars);alert('Built' if ok else 'Error'+msg)
def bind():
    m={'btn-run':run_all,'btn-execute':execute_only,'btn-patch':patch,'btn-build':build,'btn-log':toggle,'btn-variable':varp,'btn-package':package}
    for id,fn in m.items():
        e=document.getElementById(id)
        if e:e.addEventListener('click',create_proxy(lambda ev,f=fn:f()))
    console.log('Bound')
bind()