import os
import subprocess
import glob
import csv
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin

from api.app import db
from api.models import (
    Scan,
    AccessPoint,
    Station,
    ScanAccessPoint,
    ScanStation
)
from api.scan_import import parse_datetime, get_vendor_and_camera_info, SCAN_FOLDER

# Blueprint für gezielten AccessPoint-Scan
scan_ap = Blueprint('scan_ap', __name__)

# Pfad zum Bash-Skript
SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../scripts/scan_ap.sh')
)

@scan_ap.route('/scans/<int:scan_id>/scan_ap', methods=['POST', 'OPTIONS'])
@cross_origin()
def scan_single_ap(scan_id):
    """
    Führt einen gezielten Scan für einen einzelnen Access Point (BSSID) durch.
    Erwartet JSON-Body: { "bssid": "AA:BB:CC:DD:EE:FF", "channel": 6 }
    """
    data = request.get_json() or {}
    target_bssid = data.get('bssid')
    target_channel = data.get('channel')
    if not target_bssid:
        return jsonify({'error': 'bssid ist erforderlich'}), 400

    # Lade Scan-Metadaten
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan nicht gefunden'}), 404

    # Bestimme Dauer und SUDO_SECRET
    # Bestimme Dauer und SUDO_SECRET
    # Zuerst aus dem Request, falls vorhanden, sonst aus scan.duration, sonst Default
    default_duration = current_app.config.get('DEFAULT_SCAN_DURATION', 60)
    req_dur = data.get('duration')
    try:
        duration = int(req_dur) if req_dur is not None else (scan.duration or default_duration)
    except (ValueError, TypeError):
        duration = scan.duration or default_duration    
        
    secret   = current_app.config.get('SUDO_SECRET', '')

    # Baue Kommando
    cmd = [
        'sudo', '-n', 'bash', SCRIPT_PATH,
        str(duration), secret, target_bssid
    ]
    if target_channel:
        cmd.append(str(target_channel))

    current_app.logger.info(f"🔍 Starte AP-Scan: {' '.join(cmd)}")
    try:
        # Leitet Output direkt ins Leere, um RAM zu schonen
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=int(duration) + 1
        )
        scan_output = ''
    except Exception as e:
        scan_output = f"Fehler beim gezielten Scan: {e}"

    # Importiere die neue CSV in die DB
    _import_single_ap(scan_id, target_bssid)

    return jsonify({
        'scan_id': scan_id,
        'bssid': target_bssid,
        'channel': target_channel,
        'output': scan_output
    }), 200


def _import_single_ap(scan_id: int, bssid: str) -> None:
    """
    Parsed die neueste CSV für diesen BSSID und aktualisiert
    ScanAccessPoint und ScanStation für das gegebene scan_id.
    Bereits importierte Dateien werden nach dem Import verschoben.
    """
    # Finde alle passenden CSV-Dateien
    pattern = f"scan_{bssid.replace(':','')}_*.csv"
    matches = glob.glob(os.path.join(SCAN_FOLDER, pattern))
    if not matches:
        current_app.logger.warning(f"Kein CSV zum Import für BSSID {bssid} gefunden.")
        return

    # Wähle die jüngste Datei
    csv_path = max(matches, key=os.path.getmtime)

    # Verzeichnis für verarbeitete Dateien
    processed_dir = os.path.join(SCAN_FOLDER, 'imported')
    os.makedirs(processed_dir, exist_ok=True)
    dest_path = os.path.join(processed_dir, os.path.basename(csv_path))
    try:
        os.replace(csv_path, dest_path)
        csv_path = dest_path
    except Exception as e:
        current_app.logger.error(f"Fehler beim Verschieben der CSV: {e}")
        # falls Verschieben fehlschlägt, trotzdem Original verwenden

    # Lade (und erstelle ggf.) den AccessPoint
    ap = db.session.scalar(AccessPoint.select().filter_by(bssid=bssid))
    if not ap:
        ap = AccessPoint(bssid=bssid, essid=None, manufacturer=None, is_camera=False)
        db.session.add(ap)
        db.session.flush()

    # --- NEU: Existierende Stations ermitteln, um Duplikate zu vermeiden ---
    existing_macs = {
        st.mac for st in
        db.session.query(Station.mac)
          .join(ScanStation, Station.id == ScanStation.station_id)
          .filter(ScanStation.scan_id == scan_id, ScanStation.bssid == bssid)
          .all()
    }

    sap_rows = []
    sst_rows = []

    with open(csv_path, newline='', encoding='utf-8', errors='ignore') as f:
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
                # AccessPoint-Metadaten updaten
                if header == 'bssid':
                    continue
                vendor, is_cam = get_vendor_and_camera_info(row[0].strip())
                ap.manufacturer = vendor
                ap.is_camera = is_cam

                # Wir ersetzen das alte SAP-Row-Set komplett,
                # damit alle AP-Felder frisch geschrieben werden.
                sap_rows.append({
                    'scan_id': scan_id,
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
                if header == 'station mac':
                    continue
                mac = row[0].strip().upper()
                # bereits importierte Station überspringen
                if mac in existing_macs:
                    continue

                vendor, is_cam = get_vendor_and_camera_info(mac)
                station = db.session.scalar(Station.select().filter_by(mac=mac))
                if station:
                    station.manufacturer = vendor
                    station.is_camera = is_cam
                else:
                    station = Station(mac=mac, manufacturer=vendor, is_camera=is_cam)
                    db.session.add(station)
                    db.session.flush()

                sst_rows.append({
                    'scan_id': scan_id,
                    'station_id': station.id,
                    'first_seen': parse_datetime(row[1]),
                    'last_seen': parse_datetime(row[2]),
                    'power': int(row[3] or 0),
                    'packets': int(row[4] or 0),
                    'bssid': bssid,
                    'probed_essids': ', '.join(row[6:]).strip() or None
                })

    # Alte SAP-Einträge für diesen AP komplett ersetzen
    db.session.query(ScanAccessPoint).filter_by(
        scan_id=scan_id,
        access_point_id=ap.id
    ).delete()

    # Bulk-Insert für AccessPoint-Daten
    if sap_rows:
        db.session.bulk_insert_mappings(ScanAccessPoint, sap_rows)

    # Nur die **neuen** Stations hinzufügen
    if sst_rows:
        db.session.bulk_insert_mappings(ScanStation, sst_rows)

    db.session.commit()
    current_app.logger.info(f"✅ Import für BSSID {bssid} abgeschlossen.")