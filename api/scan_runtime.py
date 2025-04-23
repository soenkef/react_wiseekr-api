from flask import Blueprint, request, jsonify
import subprocess
import shlex

scan_runtime = Blueprint('scan_runtime', __name__)

@scan_runtime.route('/scan/start', methods=['POST'])
def start_scan():
    try:
        data = request.get_json()
        duration = int(data.get('duration', 30))

        # safer command execution using shlex
        command = f"timeout {duration} top -b -n 1"
        result = subprocess.run(shlex.split(command), capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({"output": result.stdout})
        else:
            return jsonify({"error": result.stderr or "Fehler beim Ausführen."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
