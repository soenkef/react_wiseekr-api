import subprocess
from flask import Blueprint, jsonify, current_app
from api.scan_import import import_all_scans
import os
from api.scan_import import SCAN_FOLDER
import time
from flask import request
from subprocess import TimeoutExpired

scan_runtime = Blueprint('scan_runtime', __name__)

@scan_runtime.route('/scan/start', methods=['POST'])
def start_scan():
    # 1. JSON-Payload parsen
    data        = request.get_json() or {}
    duration    = data.get('duration')
    location    = data.get('location', 'unknown')
    description = data.get('description')

    # 2. Secret und Script-Pfad
    secret      = current_app.config.get('SUDO_SECRET', '')
    SCRIPT_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../scripts/scan_aircrack.sh')
    )

    try:
        # 3. sudo -S bash script … duration, Passwort über stdin
        try:
            print(f"Starting scan with duration: {duration} seconds")
            
            
            result = subprocess.run(
                ['sudo','-n','bash', SCRIPT_PATH, str(duration)],
                input=secret + '\n',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=int(duration) + 15
            )            
            
            # result = subprocess.run(
            #     ['sudo','-n','bash', SCRIPT_PATH, str(duration)],
            #     input=secret + '\n',
            #     capture_output=True,
            #     text=True,
            #     timeout=int(duration) + 15  # maximal Dauer + Puffer
            # )
            result.check_returncode()
        except TimeoutExpired:
            return jsonify({"error": "Der Scan hat zu lange gedauert und wurde abgebrochen."}), 500

        # 4. Import mit Metadaten
        import_all_scans(
            description=description,
            duration=duration,
            location=location,
        )

        # 5. Erfolgreiche Antwort mit echtem Script-Output
        output = result.stdout.strip() if result.stdout is not None else ''
        return jsonify({
            "status": "ok",
            "output": output,
            "scan": {
                "description": description,
                "duration": duration,
                "location": location,
            }
        }), 200

    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Scan fehlgeschlagen: {e.stderr.strip()}")
        return jsonify({"error": e.stderr.strip() or e.stdout.strip()}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


