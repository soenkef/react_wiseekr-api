from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import subprocess
import os
import netifaces
import uuid

from api.app import db
from api.models import DeauthAction

scan_deauth_client = Blueprint('scan_deauth_client', __name__)

@scan_deauth_client.route('/deauth/client-start', methods=['POST', 'OPTIONS'])
@current_app.ensure_sync  # allow async context if needed
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
        scan_id = data.get('scan_id')
        ap_mac = data.get('ap_mac')
        client_mac = data.get('client_mac')
        channel = int(data.get('channel', 6))
        packets = int(data.get('packets', 100))
        duration = int(data.get('duration', 60))
        secret = current_app.config.get('SUDO_SECRET', '')

        if not (scan_id and ap_mac and client_mac):
            return jsonify({'error': 'scan_id, ap_mac und client_mac sind erforderlich'}), 400

        interface = 'wlan0'
        if interface not in netifaces.interfaces():
            return jsonify({'error': 'Keine WLAN-Schnittstelle gefunden'}), 400

        # Pfad zum Deauth-Skript
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        script = os.path.join(base, 'aireplay-ng_deauth_client.sh')

        # Unique ID für Logging
        uid = uuid.uuid4().hex

        cmd = [
            'bash', script,
            interface,
            ap_mac,
            client_mac,
            str(channel),
            str(packets),
            str(secret)
        ]
        current_app.logger.info(f"🔌 Deauth Client: {' '.join(cmd)}")

        # Starte Deauth
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 5)
        success = proc.returncode == 0
        output = proc.stdout.strip() or proc.stderr.strip()

        # Speichere Action
        action = DeauthAction(
            scan_id=scan_id,
            mac=client_mac,
            is_client=True,
            packets=packets,
            duration=duration,
            result_file=None,
            success=success,
            started_at=datetime.utcnow()
        )
        db.session.add(action)
        db.session.commit()

        return jsonify({
            'message': 'Client-Deauth ' + ('erfolgreich' if success else 'fehlgeschlagen'),
            'ap_mac': ap_mac,
            'client_mac': client_mac,
            'success': success,
            'output': output
        }), 200

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout beim Deauth-Prozess'}), 500
    except Exception as e:
        current_app.logger.error(f"Fehler Deauth Client: {e}")
        return jsonify({'error': str(e)}), 500
