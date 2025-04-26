import os
import csv
import glob
import time
from datetime import datetime
from flask import Blueprint, jsonify, current_app
from flask_cors import cross_origin
from sqlalchemy.exc import OperationalError
from api.app import db
from api.models import Scan, AccessPoint, Station, ScanAccessPoint, ScanStation
from netaddr import EUI, NotRegisteredError
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from api.utils.oui import OUI_MAP

# Lade Umgebungsvariablen (falls benötigt)
load_dotenv()

SCAN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scans'))

# Hilfsfunktionen

def parse_datetime(raw: str) -> datetime | None:
    raw = raw.strip()
    return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S') if raw else None


def get_vendor_and_camera_info(mac: str) -> tuple[str | None, bool]:
    # normalisiere MAC für Lookup: 'AA:BB:CC:DD:EE:FF' → 'aa:bb:cc'
    prefix = mac.lower()[0:8]
    vendor = OUI_MAP.get(prefix)
    is_camera = False
    if vendor:
        is_camera = 'camera' in vendor.lower()
    return vendor, is_camera

# Blueprint
scan_data = Blueprint('scan_data', __name__)

@scan_data.route('/scans/import', methods=['POST', 'OPTIONS'])
@cross_origin()
def trigger_import():
    try:
        import_all_scans()
        return jsonify({"message": "Import abgeschlossen."}), 200
    except OperationalError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@scan_data.route('/scans', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_all_scans():
    scans = db.session.query(Scan).order_by(Scan.id.desc()).all()
    return jsonify([
        {"id": s.id, "filename": s.filename, "description": s.description,
         "created_at": s.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for s in scans
    ])

@scan_data.route('/scans/<int:scan_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_scan_detail(scan_id):
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404
    # Detail-Logik unverändert beibehalten
    aps = db.session.query(ScanAccessPoint).options(
        joinedload(ScanAccessPoint.access_point)
    ).filter_by(scan_id=scan_id).all()
    stations = db.session.query(ScanStation).options(
        joinedload(ScanStation.station)
    ).filter_by(scan_id=scan_id).all()
    # ... Rest deiner bestehenden Mapping-Logik ...
    
    # Beispielrückgabe (anpassen wie bisher)
    ap_map = {}
    for ap in aps:
        ap_map[ap.access_point.bssid] = {
            "bssid": ap.access_point.bssid,
            "essid": ap.access_point.essid,
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
            "clients": []
        }

    unlinked = []
    for st in stations:
        client = {
            "mac": st.station.mac,
            "vendor": st.station.manufacturer,
            "is_camera": st.station.is_camera,
            "mac": st.station.mac,
            "power": st.power,
            "first_seen": st.first_seen,
            "last_seen": st.last_seen,
            "probed_essids": st.probed_essids
        }
        if st.bssid and st.bssid in ap_map:
            ap_map[st.bssid]["clients"].append(client)
        else:
            unlinked.append(client)

    return jsonify({
        "id": scan.id,
        "filename": scan.filename,
        "description": scan.description,
        "created_at": scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "access_points": list(ap_map.values()),
        "unlinked_clients": unlinked
    })

# Import-Funktion mit Bulk-Inserts und lokalem Vendor-Lookup

def import_all_scans():
    files = glob.glob(os.path.join(SCAN_FOLDER, 'scan_*.csv'))
    all_sap, all_sst = [], []

    for path in files:
        filename = os.path.basename(path)
        current_app.logger.info(f"📥 Importiere: {filename}")

        scan = Scan(description=filename, filename=filename)
        db.session.add(scan)
        db.session.flush()  # scan.id verfügbar

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

                    ap = db.session.scalar(
                        AccessPoint.select().filter_by(bssid=bssid)
                    )
                    if not ap:
                        ap = AccessPoint(
                            bssid=bssid,
                            essid=row[13].strip() or None,
                            manufacturer=vendor,
                            is_camera=is_cam
                        )
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

                    station = db.session.scalar(
                        Station.select().filter_by(mac=mac)
                    )
                    if not station:
                        station = Station(
                            mac=mac,
                            manufacturer=vendor,
                            is_camera=is_cam
                        )
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
                        'probed_essids': (', '.join(row[6:])).strip() or None
                    })

    if all_sap:
        db.session.bulk_insert_mappings(ScanAccessPoint, all_sap)
    if all_sst:
        db.session.bulk_insert_mappings(ScanStation, all_sst)
    db.session.commit()