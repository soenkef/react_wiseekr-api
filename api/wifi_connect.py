import subprocess
from flask import Blueprint, jsonify, current_app, request
from subprocess import TimeoutExpired
import re
import time

from api.app import db
from api.models import Setting

wifi_connect = Blueprint('wifi_connect', __name__)

@wifi_connect.route('/wifi/scan', methods=['GET'])
def scan_wifi():
    """Scanne verfügbare WLAN-Netzwerke via nmcli und gib Liste zurück.
    Prüfe vorher, ob NetworkManager läuft, und starte ihn bei Bedarf."""
    try:
        # 0) Prüfen, ob NetworkManager aktiv ist
        nm_status = subprocess.run(
            ['sudo', '-n', 'systemctl', 'is-active', 'NetworkManager'],
            capture_output=True, text=True, timeout=5
        )
        if nm_status.stdout.strip() != 'active':
            current_app.logger.info("NetworkManager nicht aktiv, versuche zu starten…")
            start_nm = subprocess.run(
                ['sudo', '-n', 'systemctl', 'start', 'NetworkManager'],
                capture_output=True, text=True, timeout=10
            )
            if start_nm.returncode != 0:
                current_app.logger.error(f"Fehler beim Starten des NetworkManager: {start_nm.stderr}")
                return jsonify({'error': 'NetworkManager konnte nicht gestartet werden.'}), 500
            # optional kurz warten, bis Dienst wirklich hoch ist
            time.sleep(2)

        # 1) WLAN-Scan via nmcli
        result = subprocess.run(
            ['sudo', '-n', 'nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list'],
            capture_output=True, text=True, timeout=15
        )
        result.check_returncode()

        # 2) Ausgabe parsen
        aps = []
        for line in result.stdout.splitlines():
            if ':' not in line:
                continue
            ssid, signal = line.split(':', 1)
            if ssid:
                strength = int(signal) if signal.isdigit() else 0
                aps.append({'ssid': ssid, 'strength': strength})

        return jsonify(aps), 200

    except TimeoutExpired:
        return jsonify({'error': 'Scan hat zu lange gedauert und wurde abgebrochen.'}), 500

    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Scan fehlgeschlagen: {e.stderr or e.stdout}")
        return jsonify({'error': (e.stderr or e.stdout).strip()}), 500

    except Exception as e:
        current_app.logger.error(f"Unerwarteter Fehler beim Scan: {e}")
        return jsonify({'error': str(e)}), 500

@wifi_connect.route('/wifi/status', methods=['GET'])
def wifi_status():
    """Gib aktuellen WLAN-Verbindungsstatus, IP und Gateway zurück für wlan0.
    Falls nicht verbunden und force_connect aktiv, versuche Autoconnect erneut."""
    try:
        # Aktuelle SSID und Verbindungsstatus prüfen
        ssid_proc = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, timeout=5)
        current_ssid = ssid_proc.stdout.strip()
        connected = bool(current_ssid)

        interface = 'wlan0'
        ip = ''
        gw = ''

        if connected:
            # IP ermitteln
            ip_proc = subprocess.run(
                ['ip', '-4', 'addr', 'show', 'dev', interface], capture_output=True, text=True, timeout=5
            )
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_proc.stdout)
            if match:
                ip = match.group(1)
            # Gateway ermitteln
            route_proc = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
            for ln in route_proc.stdout.splitlines():
                if ln.startswith('default ') and f'dev {interface}' in ln:
                    parts = ln.split()
                    if len(parts) >= 3:
                        gw = parts[2]
                    break
        else:
            # Autoverbindung prüfen, falls force_connect gesetzt ist
            setting = db.session.query(Setting).filter_by(force_connect=True).first()
            if setting:
                target = setting.ssid
                try:
                    # Erneut verbinden
                    cmd = ['sudo', '-n', 'nmcli', 'device', 'wifi', 'connect', target, 'ifname', 'wlan0']
                    if setting.password_hash:
                        cmd += ['password', setting.password_hash]
                    subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
                    # Bei Erfolg Status neu ermitteln
                    return wifi_status()
                except Exception as e:
                    current_app.logger.error(f"Autoconnect fehlgeschlagen für {target}: {e}")
                    # Antworte mit Zusatzinfo für Frontend
                    return jsonify({
                        'connected': False,
                        'ssid': '',
                        'ip': '',
                        'gateway': '',
                        'autoconnect_failed': True,
                        'target_ssid': target
                    }), 200

        return jsonify({
            'connected': connected,
            'ssid': current_ssid if connected else '',
            'ip': ip,
            'gateway': gw
        }), 200
    except Exception as e:
        current_app.logger.error(f"Fehler beim Abrufen des WLAN-Status: {e}")
        return jsonify({'error': str(e)}), 500

@wifi_connect.route('/ethernet/status', methods=['GET'])
def ethernet_status():
    """Gib aktuellen Ethernet-Status, IP und Gateway zurück für eth0."""
    try:
        interface = 'eth0'
        ip_proc = subprocess.run(
            ['ip', '-4', 'addr', 'show', 'dev', interface], capture_output=True, text=True, timeout=5
        )
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_proc.stdout)
        ip = match.group(1) if match else ''
        connected = bool(ip)

        gw = ''
        route_proc = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5)
        for ln in route_proc.stdout.splitlines():
            if ln.startswith('default ') and f'dev {interface}' in ln:
                parts = ln.split()
                if len(parts) >= 3:
                    gw = parts[2]
                break

        return jsonify({'connected': connected, 'ip': ip, 'gateway': gw}), 200
    except Exception as e:
        current_app.logger.error(f"Fehler beim Abrufen des Ethernet-Status: {e}")
        return jsonify({'error': str(e)}), 500

@wifi_connect.route('/settings', methods=['POST'])
def save_settings():
    """Speichere WLAN-Einstellungen, lösche alte Einträge, setze Autoconnect und verbinde."""
    data = request.get_json() or {}
    ssid = data.get('ssid')
    password = data.get('password')
    force_flag = data.get('force_connect', 0)
    try:
        force_connect = bool(int(force_flag))
    except (ValueError, TypeError):
        force_connect = False

    if not ssid:
        return jsonify({'error': 'SSID fehlt'}), 400

    try:
        # 1. Lösche alle alten Einstellungen
        db.session.query(Setting).delete()
        db.session.commit()

        # 2. Neuen Eintrag speichern
        setting = Setting(ssid=ssid, force_connect=force_connect)
        if password:
            setting.password = password
        db.session.add(setting)
        db.session.commit()

        # 3. NMCLI: Verbinden
        subprocess.run(
            ['sudo', '-n', 'nmcli', 'device', 'wifi', 'connect', ssid] + (['password', password] if password else []) + ['ifname', 'wlan0'],
            capture_output=True, text=True, timeout=30, check=True
        )

        # 4. NMCLI: Autoconnect setzen auf die korrekte Connection
        conn_list = subprocess.run(
            ['nmcli', '-t', '-f', 'NAME,UUID,TYPE', 'connection', 'show'],
            capture_output=True, text=True
        )
        conn_uuid = None
        for line in conn_list.stdout.splitlines():
            try:
                name, uuid, ctype = line.split(':', 2)
            except ValueError:
                continue
            if ctype == '802-11-wireless' and name == ssid:
                conn_uuid = uuid
                break
        if conn_uuid:
            subprocess.run(
                ['sudo', '-n', 'nmcli', 'connection', 'modify', conn_uuid,
                 'connection.autoconnect', 'yes' if force_connect else 'no'],
                capture_output=True, text=True, check=True
            )

        return jsonify({'status': 'ok', 'ssid': ssid, 'force_connect': force_connect}), 200
    except TimeoutExpired:
        current_app.logger.error(f"Timeout beim Verbinden zu {ssid}")
        return jsonify({'error': 'Timeout beim Verbinden'}), 500
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"NMCLI-Fehler: {e.stderr or e.stdout}")
        return jsonify({'error': (e.stderr or e.stdout).strip()}), 500
    except Exception as e:
        current_app.logger.error(f"Fehler beim Speichern der Settings: {e}")
        return jsonify({'error': str(e)}), 500

@wifi_connect.route('/wifi/disconnect', methods=['POST'])
def disconnect_wifi():
    """Trenne die aktuelle WLAN-Verbindung auf wlan0 und lösche gespeicherte Einstellung."""
    try:
        # 1) WLAN trennen
        subprocess.run(
            ['sudo', '-n', 'nmcli', 'device', 'disconnect', 'wlan0'],
            capture_output=True, text=True, timeout=10, check=True
        )
        # 2) gespeicherte Einstellung entfernen
        db.session.query(Setting).delete()
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
    except TimeoutExpired:
        current_app.logger.error("Timeout beim Trennen des WLANs.")
        return jsonify({'error': 'Timeout beim Trennen.'}), 500
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Fehler beim Trennen: {e.stderr or e.stdout}")
        return jsonify({'error': (e.stderr or e.stdout).strip()}), 500
    except Exception as e:
        current_app.logger.error(f"Unerwarteter Fehler beim Trennen: {e}")
        return jsonify({'error': str(e)}), 500
