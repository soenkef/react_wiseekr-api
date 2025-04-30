from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import subprocess
import shlex
import uuid
import os
import netifaces
from flask_cors import cross_origin

from api.app import db
from api.models import DeauthAction, AccessPoint

deauth_bp = Blueprint('deauth_bp', __name__)

@deauth_bp.route('/deauth/start', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth():
    try:
        data = request.get_json()
        mac = data.get("mac")
        is_client = data.get("is_client", False)
        packets = int(data.get("packets", 100))
        duration = int(data.get("duration", 60))
        scan_id = data.get("scan_id")
        secret      = current_app.config.get('SUDO_SECRET', '')

        if not mac:
            return jsonify({"error": "MAC-Adresse erforderlich"}), 400

        uid = str(uuid.uuid4())
        interface = "wlan0"
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

        aireplay_cmd = ["bash", aireplay_script, interface, mac, str(packets), str(ap_channel), str(secret)]

        airodump_proc = None
        if not is_client and packets < 9999:
            airodump_cmd = ["bash", airodump_script, interface, cap_output, str(duration), str(secret)]
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


@deauth_bp.route('/deauth/start_deauth_client', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth_client():
    """
    Führt eine Deauthentifizierung eines Client-Geräts vom Access Point durch.
    Erwartet JSON: {
      "scan_id": int,
      "ap_mac": "AA:BB:CC:DD:EE:FF",
      "client_mac": "11:22:33:44:55:66",
      "channel": int,
      "packets": int,
      "duration": int
    }
    """
    # CORS preflight
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        scan_id     = data.get('scan_id')
        ap_mac      = data.get('ap_mac')
        client_mac  = data.get('client_mac')
        channel     = int(data.get('channel', 6))
        packets     = int(data.get('packets', 100))
        duration    = int(data.get('duration', 60))
        secret      = current_app.config.get('SUDO_SECRET', '')

        if not (scan_id and ap_mac and client_mac):
            return jsonify({'error': 'scan_id, ap_mac und client_mac sind erforderlich'}), 400

        interface = 'wlan0'
        if interface not in netifaces.interfaces():
            return jsonify({'error': 'Keine WLAN-Schnittstelle gefunden'}), 400

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
        aireplay_script = os.path.join(base_path, 'aireplay-ng_deauth_client.sh')
        airodump_script = os.path.join(base_path, 'airodump-ng_handshake.sh')

        uid = uuid.uuid4().hex
        cap_output = f"handshake_scan_{uid}.cap"
        cap_path   = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../scans/{cap_output}"))

        # 1) optional: Handshake-Mitschnitt starten
        handshake_proc = None
        if packets < 9999:
            hs_cmd = [
                'sudo', '-n', 'bash', airodump_script,
                interface,
                ap_mac,
                client_mac,
                str(duration),
                str(channel),
                str(secret)
            ]
            current_app.logger.info(f"🔌 Starte Deauth Client: {client_mac} vom AP {ap_mac} auf Kanal {channel} mit {packets} Paketen für {duration} Sekunden")
            current_app.logger.info(f"🔍 Starte Handshake-Mitschnitt: {' '.join(hs_cmd)}")
            handshake_proc = subprocess.Popen(hs_cmd)
        
        time.sleep(2)  # Warten auf Airodump-Start

        # 2) Deauth-Pakete senden
        deauth_cmd = [
            'sudo', '-n', 'bash', aireplay_script,
            interface,
            ap_mac,
            client_mac,
            str(channel),
            str(packets),
            str(secret)
        ]
        current_app.logger.info(f"🔌 Deauth Packets Client: {' '.join(deauth_cmd)}")
        deauth_proc = subprocess.Popen(deauth_cmd)

        # 3) auf Ende warten
        deauth_proc.wait(timeout=duration + 5)
        if handshake_proc:
            try:
                handshake_proc.wait(timeout=duration + 5)
            except subprocess.TimeoutExpired:
                current_app.logger.warning("🤚 Handshake-Mitschnitt abgebrochen (Timeout)")

        # 4) prüfen auf Handshake-Datei
        handshake_found = os.path.exists(cap_path) and os.path.getsize(cap_path) > 0

        # 5) in DB speichern
        action = DeauthAction(
            scan_id=scan_id,
            mac=client_mac,
            is_client=True,
            packets=packets,
            duration=duration,
            result_file=cap_output if handshake_found else None,
            success=handshake_found,
            started_at=datetime.utcnow()
        )
        db.session.add(action)
        db.session.commit()

        return jsonify({
            'message':   'Client-Deauth ' + ('erfolgreich' if handshake_found else 'fehlgeschlagen'),
            'ap_mac':    ap_mac,
            'client_mac': client_mac,
            'success':   handshake_found,
            'file':      cap_output if handshake_found else None
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout beim Deauth-Prozess.'}), 500
    except Exception as e:
        current_app.logger.error(f"Fehler Deauth Client: {e}")
        return jsonify({'error': str(e)}), 500