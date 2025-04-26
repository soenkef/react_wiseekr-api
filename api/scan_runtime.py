import subprocess
from flask import Blueprint, jsonify, current_app
from api.scan_import import import_all_scans
import os
from api.scan_import import SCAN_FOLDER
import time
from flask import request

scan_runtime = Blueprint('scan_runtime', __name__)

@scan_runtime.route('/scan/start', methods=['POST'])
def start_scan():
    try:
        #SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/scan.sh'))
        #subprocess.run(['bash', SCRIPT_PATH], check=True)
        import_all_scans()
        return jsonify({"status": "ok"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500
    

@scan_runtime.route('/scan/rescan', methods=['POST'])
def scan_ap():
    data = request.get_json()
    duration = data.get('duration', 60)
    prefix = data.get('prefix', f"scan_{int(time.time())}")
    secret = current_app.config['SUDO_SECRET']  # z.B. als Umgebungsvariable geladen

    script_path = os.path.join(os.path.dirname(__file__), '../static/wifi/scripts/scan_ap.sh')
    try:
        #subprocess.run(['bash', script_path, str(duration), secret, prefix], check=True)
        return jsonify({
            "status": "ok",
            "files": [f"{prefix}-01.csv", f"{prefix}-01.kismet.csv"]
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


