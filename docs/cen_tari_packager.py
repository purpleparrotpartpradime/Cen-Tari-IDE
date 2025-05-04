# cen_tari_packager.py
import os, tempfile, subprocess, sys
def make_exe(python_code: str, variables: dict=None):
    try:
        tmpdir = tempfile.mkdtemp()
        script_path = os.path.join(tmpdir, "app.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("from cen_tari_runtime import execute_cen_tari\n")
            f.write("if __name__=='__main__':\n")
            for n,v in (variables or {}).items():
                f.write(f"    {n} = {repr(v)}\n")
            f.write(f"    execute_cen_tari('''{python_code}''', show_ui=False)")
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", script_path], check=True)
        exe_path = os.path.join(tmpdir, "dist", "app.exe" if os.name=="nt" else "app")
        return True, exe_path
    except Exception as e:
        return False, str(e)
