from flask import Blueprint, request, jsonify
import subprocess
import uuid
import os

scan_runtime = Blueprint('scan_runtime', __name__)

@scan_runtime.route('/scan/start', methods=['POST'])
def start_scan():
    try:
        data = request.get_json()
        duration = int(data.get('duration', 30))

        scan_id = str(uuid.uuid4())
        script_path = os.path.join(os.path.dirname(__file__), '../scripts/scan_aircrack.sh')

        # Aufruf des Bash-Skripts mit Dauer als Argument
        result = subprocess.run([
            'bash', script_path, str(duration)
        ], capture_output=True, text=True)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        print("SCRIPT STDOUT:", stdout)
        print("SCRIPT STDERR:", stderr)
        print("SCRIPT RETURN CODE:", result.returncode)

        if result.returncode == 0:
            return jsonify({"output": stdout})

        # Fehlerbehandlung basierend auf bekannter Ausgaben
        error_msgs = []
        if "Interface wlan1 not found" in stdout or "Interface wlan1 not found" in stderr:
            error_msgs.append("Wlan-device not present")
        if "command not found" in stdout or "command not found" in stderr or "airodump-ng: not found" in stderr:
            error_msgs.append("Scan-Error due missing dependencies")

        # Kombinierte Meldung
        if error_msgs:
            return jsonify({"error": " and ".join(error_msgs)}), 500

        return jsonify({"error": stderr or "Scan fehlgeschlagen."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
