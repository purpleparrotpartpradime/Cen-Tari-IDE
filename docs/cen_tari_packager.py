# cen_tari_packager.py
import os,tempfile,subprocess,sys
def make_exe(code,variables=None):
    d=tempfile.mkdtemp();p=os.path.join(d,'app.py')
    with open(p,'w')as f:
        f.write("from cen_tari_runtime import execute_cen_tari\nif __name__=='__main__':\n")
        for k,v in(variables or{}).items():f.write(f"    {k}={v!r}\n")
        f.write(f"    execute_cen_tari('''{code}''',show_ui=False)")
    subprocess.run([sys.executable,'-m','PyInstaller','--onefile',p],check=True)
    exe=os.path.join(d,'dist','app.exe'if os.name=='nt'else'app')
    return True,exe