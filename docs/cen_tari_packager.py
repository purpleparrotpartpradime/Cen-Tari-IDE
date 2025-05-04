# cen_tari_packager.py
import os
import tempfile
import subprocess
import sys

def make_exe(python_code: str, variables: dict=None):
    try:
        tmpdir = tempfile.mkdtemp()
        script_path = os.path.join(tmpdir, "app.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("import sys\n")
            f.write("from cen_tari_runtime import execute_cen_tari\n")
            f.write("from cen_tari_translator import translate\n\n")
            f.write("if __name__=='__main__':\n")
            if variables:
                for name, val in variables.items():
                    f.write(f"    {name} = {repr(val)}\n")
            f.write("    code = '''\\\n" + python_code + "\n'''\n")
            f.write("    execute_cen_tari(code, show_ui=False)\n")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--distpath", tmpdir,
            "--workpath", os.path.join(tmpdir, "build"),
            "--specpath", tmpdir,
            script_path
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return False, proc.stderr
        exe_name = "app.exe" if os.name=="nt" else "app"
        exe_path = os.path.join(tmpdir, exe_name)
        if not os.path.exists(exe_path):
            base = os.path.splitext(os.path.basename(script_path))[0]
            exe_path = os.path.join(tmpdir, base + (".exe" if os.name=="nt" else ""))
        return True, exe_path
    except Exception as e:
        return False, str(e)
