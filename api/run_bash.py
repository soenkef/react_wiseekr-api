from api import db


import subprocess

def run_scan_script():
    try:
        result = subprocess.run(
            ["bash", "scripts/run_scan.sh"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"output": result.stdout, "error": None}
    except subprocess.CalledProcessError as e:
        return {"output": e.stdout, "error": e.stderr}