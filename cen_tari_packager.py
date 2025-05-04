# cen_tari_packager.py
import os
import tempfile
import subprocess
import sys

def make_exe(python_code: str, variables: dict = None):
    """
    Writes a temporary Python script combining:
      - this runtime
      - the translated code
    Then calls PyInstaller to bundle it into a single EXE.
    Returns (success: bool, message: str).
    """
    try:
        tmpdir = tempfile.mkdtemp()
        script_path = os.path.join(tmpdir, "app.py")

        # Write the combined script
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("import sys\n")
            f.write("from cen_tari_runtime import execute_cen_tari\n")
            f.write("from cen_tari_translator import translate\n\n")
            f.write("if __name__=='__main__':\n")
            # inject variables
            if variables:
                for name, val in variables.items():
                    f.write(f"    {name} = {repr(val)}\n")
            f.write("    code = '''\\\n" + python_code + "\n'''\n")
            f.write("    execute_cen_tari(code, show_ui=False)\n")

        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--distpath", tmpdir,
            "--workpath", os.path.join(tmpdir, "build"),
            "--specpath", tmpdir,
            script_path
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return False, proc.stderr

        # Find the .exe
        exe_name = "app.exe" if os.name == "nt" else "app"
        exe_path = os.path.join(tmpdir, exe_name)
        if not os.path.exists(exe_path):
            # PyInstaller names after script by default
            base = os.path.splitext(os.path.basename(script_path))[0]
            alt = os.path.join(tmpdir, base + (".exe" if os.name=="nt" else ""))
            exe_path = alt

        return True, exe_path
    except Exception as e:
        return False, str(e)
