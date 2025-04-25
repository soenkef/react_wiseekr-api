import os
import csv
from datetime import datetime
from api.app import db
from api.models import Scan, AccessPoint, Station, ScanAccessPoint, ScanStation
import requests
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der .env Datei
load_dotenv()
API_KEY = os.getenv("MACADDRESS_API_TOKEN")
MAC_VENDORS_API_URL = "https://api.macvendors.com/"


SCAN_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scans'))

def parse_datetime(raw):
    return datetime.strptime(raw.strip(), '%Y-%m-%d %H:%M:%S') if raw.strip() else None


def import_all_scans():
    for filename in os.listdir(SCAN_FOLDER):
        if filename.endswith('.csv') and filename.startswith('scan_'):
            path = os.path.join(SCAN_FOLDER, filename)
            print(f"📥 Importiere: {filename}")
            import_single_scan(path, filename)
    db.session.commit()

def get_vendor_and_camera_info(mac_address):
    # Abfrage des Herstellers über die API (z.B. macvendors)
    try:
        vendor = requests.get(f"{MAC_VENDORS_API_URL}/{mac_address}").text
        # Hier können wir eine eigene Logik einbauen, um zu prüfen, ob es sich um eine Kamera handelt.
        is_camera = "camera" in vendor.lower()  # Eine einfache Annahme, dass "camera" im Vendor-String vorkommt
        return vendor, is_camera
    except Exception as e:
        return None, False  # Falls keine Information gefunden wird, keine Kamera

def import_single_scan(filepath, filename):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        lines = list(reader)

    if not lines:
        return

    scan = Scan(description="Imported scan", filename=filename)
    db.session.add(scan)
    db.session.flush()  # ID verfügbar

    ap_mode = True
    for i, row in enumerate(lines):
        if len(row) < 2:
            continue
        if 'Station MAC' in row[0]:
            ap_mode = False
            continue

        if ap_mode:
            if len(row) < 14 or row[0].lower() == 'bssid':
                continue
            bssid = row[0].strip()
            ap = db.session.scalar(AccessPoint.select().where(AccessPoint.bssid == bssid))
            if not ap:
                ap = AccessPoint(
                    bssid=bssid,
                    essid=row[13].strip() or None
                )
                db.session.add(ap)
                db.session.flush()

            # Hersteller und Kameraerkennung
            vendor, is_camera = get_vendor_and_camera_info(bssid)
            ap.manufacturer = vendor
            ap.is_camera = is_camera  # Setze den Wert für die Kameraerkennung

            sap = ScanAccessPoint(
                scan_id=scan.id,
                access_point_id=ap.id,
                first_seen=parse_datetime(row[1]),
                last_seen=parse_datetime(row[2]),
                channel=int(row[3] or 0),
                speed=int(row[4] or 0),
                privacy=row[5].strip() or None,
                cipher=row[6].strip() or None,
                authentication=row[7].strip() or None,
                power=int(row[8] or 0),
                beacons=int(row[9] or 0),
                iv=int(row[10] or 0),
                lan_ip=row[11].strip() or None,
                id_length=int(row[12] or 0),
                key=row[14].strip() or None
            )
            db.session.add(sap)

        else:
            if len(row) < 6 or row[0].lower() == 'station mac':
                continue
            mac = row[0].strip()
            station = db.session.scalar(Station.select().where(Station.mac == mac))
            if not station:
                station = Station(mac=mac)
                db.session.add(station)
                db.session.flush()

            # Hersteller und Kameraerkennung für Clients
            vendor, is_camera = get_vendor_and_camera_info(mac)
            station.manufacturer = vendor
            station.is_camera = is_camera  # Setze den Wert für die Kameraerkennung

            sst = ScanStation(
                scan_id=scan.id,
                station_id=station.id,
                first_seen=parse_datetime(row[1]),
                last_seen=parse_datetime(row[2]),
                power=int(row[3] or 0),
                packets=int(row[4] or 0),
                bssid=row[5].strip() or None,
                probed_essids=(', '.join(row[6:])).strip() if len(row) > 6 else None
            )
            db.session.add(sst)

    db.session.commit()


# --- API für das Frontend ---
from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload
from flask_cors import cross_origin

scan_data = Blueprint('scan_data', __name__)

@scan_data.route('/scans/import', methods=['POST', 'OPTIONS'])
@cross_origin()
def trigger_import():
    try:
        import_all_scans()
        return jsonify({"message": "Import abgeschlossen."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scan_data.route('/scans', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_all_scans():
    scans = db.session.query(Scan).order_by(Scan.id.desc()).all()
    return jsonify([{
        "id": s.id,
        "filename": s.filename,
        "description": s.description,
        "created_at": s.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    } for s in scans])


@scan_data.route('/scans/<int:scan_id>', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_scan_detail(scan_id):
    scan = db.session.get(Scan, scan_id)
    if not scan:
        return jsonify({'error': 'Scan not found'}), 404

    aps = db.session.query(ScanAccessPoint).options(
        joinedload(ScanAccessPoint.access_point)
    ).filter_by(scan_id=scan_id).all()

    stations = db.session.query(ScanStation).options(
        joinedload(ScanStation.station)
    ).filter_by(scan_id=scan_id).all()

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
        obj = {
            "mac": st.station.mac,
            "power": st.power,
            "first_seen": st.first_seen,
            "last_seen": st.last_seen,
            "probed_essids": st.probed_essids
        }
        if st.bssid and st.bssid in ap_map:
            ap_map[st.bssid]["clients"].append(obj)
        else:
            unlinked.append(obj)

    return jsonify({
        "id": scan.id,
        "filename": scan.filename,
        "description": scan.description,
        "access_points": list(ap_map.values()),
        "unlinked_clients": unlinked
    })