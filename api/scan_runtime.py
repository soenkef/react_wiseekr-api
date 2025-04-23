import subprocess
from flask import Blueprint, jsonify
from api.scan_import import import_all_scans
import os

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
