from flask import Blueprint, request, jsonify
from datetime import datetime
import subprocess
import shlex
import uuid
import os
import netifaces

from api.app import db
from api.models import DeauthAction, AccessPoint

scan_deauth = Blueprint('scan_deauth', __name__)

@scan_deauth.route('/deauth/start', methods=['POST'])
def start_deauth():
    try:
        data = request.get_json()
        mac = data.get("mac")
        is_client = data.get("is_client", False)
        packets = int(data.get("packets", 100))
        duration = int(data.get("duration", 60))
        scan_id = data.get("scan_id")

        if not mac:
            return jsonify({"error": "MAC-Adresse erforderlich"}), 400

        uid = str(uuid.uuid4())
        interface = "wlan1"
        if interface not in netifaces.interfaces():
            return jsonify({"error": "No wifi component detected"}), 400
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))

        aireplay_script = os.path.join(base_path, "aireplay-ng_deauth.sh")
        airodump_script = os.path.join(base_path, "airodump-ng_handshake.sh")
        cap_output = f"handshake_scan_{uid}.cap"
        cap_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../scans/{cap_output}"))

        # Versuche Kanal aus AccessPoint-Datenbankeintrag zu ermitteln
        ap = db.session.query(AccessPoint).filter_by(scan_id=scan_id, bssid=mac).first()
        ap_channel = ap.channel if ap else 6  # fallback auf Kanal 6

        aireplay_cmd = ["bash", aireplay_script, interface, mac, str(packets), str(ap_channel)]

        airodump_proc = None
        if not is_client and packets < 9999:
            airodump_cmd = ["bash", airodump_script, interface, cap_output, str(duration)]
            airodump_proc = subprocess.Popen(airodump_cmd)

        deauth_proc = subprocess.Popen(aireplay_cmd)

        deauth_proc.wait(timeout=duration + 5)
        if airodump_proc:
            airodump_proc.wait(timeout=duration + 5)

        handshake_found = os.path.exists(cap_path) and os.path.getsize(cap_path) > 0

        action = DeauthAction(
            scan_id=scan_id,
            mac=mac,
            is_client=is_client,
            packets=packets,
            duration=duration,
            result_file=cap_output if handshake_found else None,
            success=handshake_found,
            started_at=datetime.utcnow()
        )
        db.session.add(action)
        db.session.commit()

        if handshake_found:
            return jsonify({
                "message": "Deauth erfolgreich, Handshake gefunden.",
                "file": cap_output,
                "mac": mac,
                "success": True
            })
        else:
            return jsonify({
                "message": "Deauth abgeschlossen, kein Handshake gefunden.",
                "mac": mac,
                "success": False
            })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Timeout beim Deauth-Prozess."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
