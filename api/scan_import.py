import os
import csv
import glob
import time
import subprocess
from datetime import datetime
from flask import Blueprint, jsonify, current_app, request
from flask_cors import cross_origin
from sqlalchemy.exc import OperationalError
from api.app import db
from api.models import Scan, AccessPoint, Station, ScanAccessPoint, ScanStation, DeauthAction, Setting
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from api.utils.oui import OUI_MAP
from api.utils.camera import CAMERA_MANUFACTURERS

# Lade Umgebungsvariablen (falls benötigt)
load_dotenv()

SCAN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scans'))
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/scan_aircrack.sh'))

# Hilfsfunktionen
def parse_datetime(raw: str) -> datetime | None:
    raw = raw.strip()
    return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S') if raw else None


def get_vendor_and_camera_info(mac: str) -> tuple[str | None, bool]:
    mac_norm = mac.lower().replace('-', ':')
    prefix = mac_norm.replace(':', '')[:6]
    vendor = OUI_MAP.get(prefix)

    is_camera = False
    if vendor:
        vendor_lower = vendor.lower()
        for cam_name in CAMERA_MANUFACTURERS:
            if cam_name.lower() in vendor_lower:
                is_camera = True
                break

    return vendor, is_camera

# Blueprint
scan_data = Blueprint('scan_data', __name__)

@scan_data.route('/scans/import', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def trigger_import():
    # CORS preflight
    if current_app.request.method == 'OPTIONS':
        return '', 200

    # 1) Prüfen, ob bereits ein Scan läuft
    running = db.session.query(Scan).filter_by(is_active=True).first()
    if running:
        return jsonify({"error": "Ein Scan läuft bereits (ID: %d)." % running.id}), 400

    # 2) Markiere global „Scan läuft“
    #    – hier könnte man auch eine eigene Status-Tabelle nehmen, 
    #      wir schreiben es direkt in den neuen Scan-Datensatz.
    try:
        # Starte Import/Scan und erhalte die neuen Scan-Objekte zurück
        new_scans = import_all_scans(return_scans=True)
        # import_all_scans sollte dann in seinen Insert-Flows am Scan-Objekt
        # `scan.is_active = True` setzen, bevor es `db.session.commit()` tut.

        # --- Beispiel, falls import_all_scans nur scan-IDs zurückgibt: ---
        for scan in new_scans:
            scan.is_active = True
            db.session.add(scan)
        db.session.commit()

        # 3) Hier führst du tatsächlichen Scan durch (z.B. Shell-Skript), 
        #    oder bei reinen CSV-Importen ist dieser Schritt schon erledigt.

        # 4) Nach Abschluss alle neuen Scans freigeben
        for scan in new_scans:
            scan.is_active = False
            db.session.add(scan)
        db.session.commit()

        return jsonify({"message": "Import/Scan abgeschlossen."}), 200

    except OperationalError as e:
        # bei DB-Fehlern ebenfalls freigeben
        for scan in new_scans:
            scan.is_active = False
            db.session.add(scan)
        db.session.commit()
        current_app.logger.error(f"DB-Error beim Import: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # alles andere auch freigeben und zurückrollen
        db.session.rollback()
        current_app.logger.error(f"Fehler beim Import: {e}")
        return jsonify({"error": str(e)}), 500

@scan_data.route('/scans', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_all_scans():
    scans = db.session.query(Scan).order_by(Scan.id.desc()).all()
    # Debug-Log: wie viele AP-Einträge gibt es insgesamt?
    #total_aps = db.session.query(ScanAccessPoint).count()
    #current_app.logger.debug(f"⭐️ Insgesamt {total_aps} ScanAccessPoint-Datensätze in der DB")

    result = []
    for s in scans:
        # Anzahl der AccessPoints ermitteln
        ap_count = db.session.query(ScanAccessPoint) \
            .filter_by(scan_id=s.id) \
            .count()
        #current_app.logger.debug(f"🔍 Scan {s.id} => {ap_count} APs")
        
        result.append({
            "id": s.id,
            "filename": s.filename,
            "description": s.description,
            "location": s.location,
            "created_at": s.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "access_points_count": ap_count
        })
    return jsonify(result)

@scan_data.route('/scans/<int:scan_id>', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def get_scan_detail(scan_id):
    # 1) Lade den Scan
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404

    # 2) Optional: gezielten Einzel-Scan ausführen
    target_bssid = request.args.get('bssid')
    target_channel = request.args.get('channel')
    scan_output = None
    if target_bssid:
        secret = current_app.config.get('SUDO_SECRET', '')
        cmd = ['sudo', '-n', 'bash', SCRIPT_PATH, str(scan.duration), secret, target_bssid]
        if target_channel:
            cmd.append(target_channel)
        current_app.logger.info(f"🔍 Starte gezielten Scan: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(scan.duration) + 15
            )
            scan_output = result.stdout.strip() if result.stdout else ''
        except Exception as e:
            scan_output = f"Fehler beim gezielten Scan: {e}"

    # 3) Hole alle AccessPoints & Stations
    aps = db.session.query(ScanAccessPoint).options(
        joinedload(ScanAccessPoint.access_point)
    ).filter_by(scan_id=scan_id).all()
    stations = db.session.query(ScanStation).options(
        joinedload(ScanStation.station)
    ).filter_by(scan_id=scan_id).all()

    # 4) Lade Deauth-Aktionen für Handshake-Dateien
    actions = db.session.query(DeauthAction).filter_by(scan_id=scan_id).all()
    deauth_map = {a.mac: a.handshake_file for a in actions if a.handshake_file}

    # 5) Baue die Access Point–Map
    ap_map: dict[str, dict] = {}
    for ap in aps:
        ap_map[ap.access_point.bssid] = {
            "bssid": ap.access_point.bssid,
            "essid": ap.access_point.essid,
            "vendor": ap.access_point.manufacturer,
            "is_camera": ap.access_point.is_camera,
            "channel": ap.channel,
            "first_seen": ap.first_seen,
            "last_seen": ap.last_seen,
            "speed": ap.speed,
            "privacy": ap.privacy,
            "cipher": ap.cipher,
            "authentication": ap.authentication,
            "power": ap.power,
            "beacons": ap.beacons,
            "iv": ap.iv,
            "lan_ip": ap.lan_ip,
            "id_length": ap.id_length,
            "key": ap.key,
            "clients": [],
            "handshake_file": deauth_map.get(ap.access_point.bssid)
        }

    # 6) Verteile die Stations auf APs oder unlinked
    unlinked = []
    for st in stations:
        client = {
            "mac": st.station.mac,
            "vendor": st.station.manufacturer,
            "is_camera": st.station.is_camera,
            "power": st.power,
            "first_seen": st.first_seen,
            "last_seen": st.last_seen,
            "probed_essids": st.probed_essids,
            "handshake_file": deauth_map.get(st.station.mac)
        }
        if st.bssid and st.bssid in ap_map:
            ap_map[st.bssid]["clients"].append(client)
        else:
            unlinked.append(client)

    # 7) Baue und sende die Antwort
    response = {
        "id": scan.id,
        "filename": scan.filename,
        "description": scan.description,
        "duration": scan.duration,
        "location": scan.location,
        "created_at": scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "access_points": list(ap_map.values()),
        "unlinked_clients": unlinked
    }
    if scan_output is not None:
        response["scan_output"] = scan_output
    
    # --- 8) Dateigröße der CSV hinzufügen ---
    try:
        filepath = os.path.join(SCAN_FOLDER, scan.filename)
        # in Bytes
        response["filesize"] = os.path.getsize(filepath)
    except Exception:
        # falls Datei nicht gefunden o.ä.
        response["filesize"] = None

    return jsonify(response)

# Import-Funktion mit Bulk-Inserts und lokalem Vendor-Lookup
def import_all_scans(description=None, duration=None, location=None):

    # Bereits verarbeitete Dateien ermitteln
    processed = {fname for (fname,) in db.session.query(Scan.filename).all() if fname}

    all_sap, all_sst = [], []
    files = glob.glob(os.path.join(SCAN_FOLDER, 'scan_*.csv'))
    for path in files:
        filename = os.path.basename(path)
        if filename in processed:
            current_app.logger.info(f"🚀 Überspringe bereits importierte Datei: {filename}")
            continue

        # Metadaten für den neuen Scan
        scan_meta = {
            'filename': filename,
            'description': description if description is not None else filename,
            'location': location if location is not None else 'unknown',
            'timestamp': datetime.now()
        }
        if duration is not None:
            scan_meta['duration'] = duration

        scan = Scan(**scan_meta)
        db.session.add(scan)
        db.session.flush()

        with open(path, newline='', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            ap_mode = True
            for row in reader:
                if len(row) < 2:
                    continue
                header = row[0].lower()
                if 'station mac' in header:
                    ap_mode = False
                    continue

                if ap_mode:
                    if len(row) < 14 or header == 'bssid':
                        continue
                    bssid = row[0].strip()
                    vendor, is_cam = get_vendor_and_camera_info(bssid)
                    ap = db.session.scalar(AccessPoint.select().filter_by(bssid=bssid))
                    if ap:
                        ap.manufacturer, ap.is_camera = vendor, is_cam
                        db.session.flush()
                    else:
                        ap = AccessPoint(bssid=bssid, essid=row[13].strip() or None,
                                         manufacturer=vendor, is_camera=is_cam)
                        db.session.add(ap)
                        db.session.flush()
                    all_sap.append({
                        'scan_id': scan.id,
                        'access_point_id': ap.id,
                        'first_seen': parse_datetime(row[1]),
                        'last_seen': parse_datetime(row[2]),
                        'channel': int(row[3] or 0),
                        'speed': int(row[4] or 0),
                        'privacy': row[5].strip() or None,
                        'cipher': row[6].strip() or None,
                        'authentication': row[7].strip() or None,
                        'power': int(row[8] or 0),
                        'beacons': int(row[9] or 0),
                        'iv': int(row[10] or 0),
                        'lan_ip': row[11].strip() or None,
                        'id_length': int(row[12] or 0),
                        'key': row[14].strip() or None
                    })
                else:
                    if len(row) < 6 or header == 'station mac':
                        continue
                    mac = row[0].strip()
                    vendor, is_cam = get_vendor_and_camera_info(mac)
                    station = db.session.scalar(Station.select().filter_by(mac=mac))
                    if station:
                        station.manufacturer, station.is_camera = vendor, is_cam
                        db.session.flush()
                    else:
                        station = Station(mac=mac, manufacturer=vendor, is_camera=is_cam)
                        db.session.add(station)
                        db.session.flush()
                    all_sst.append({
                        'scan_id': scan.id,
                        'station_id': station.id,
                        'first_seen': parse_datetime(row[1]),
                        'last_seen': parse_datetime(row[2]),
                        'power': int(row[3] or 0),
                        'packets': int(row[4] or 0),
                        'bssid': row[5].strip() or None,
                        'probed_essids': ', '.join(row[6:]).strip() or None
                    })

    if all_sap:
        db.session.bulk_insert_mappings(ScanAccessPoint, all_sap)
    if all_sst:
        db.session.bulk_insert_mappings(ScanStation, all_sst)

    db.session.commit()


@scan_data.route('/scans/<int:scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Löscht einen Scan mitsamt allen zugehörigen Daten und der CSV-Datei."""
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan nicht gefunden'}), 404

    try:
        # 1) Alle zugehörigen DeauthAction-, ScanAccessPoint- und ScanStation-Einträge löschen
        db.session.query(DeauthAction).filter_by(scan_id=scan_id).delete()
        db.session.query(ScanAccessPoint).filter_by(scan_id=scan_id).delete()
        db.session.query(ScanStation).filter_by(scan_id=scan_id).delete()

        # 2) Scan-Eintrag löschen
        filename = scan.filename
        db.session.delete(scan)
        db.session.commit()

        # 3) CSV-Datei vom Filesystem entfernen
        filepath = os.path.join(SCAN_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({'message': 'Scan und alle zugehörigen Daten gelöscht.'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Fehler beim Löschen des Scans: {e}")
        return jsonify({'error': str(e)}), 500