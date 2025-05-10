from flask import Blueprint, send_file, send_from_directory, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.utils import safe_join
from api.models import Scan, DeauthAction  # Passe den Import an deine Projektstruktur an
import os
from api.app import db  # Passe den Import an deine Projektstruktur an

# Blueprint für den Datei-Download
# Datei: download_file.py
download_file_bp = Blueprint('download_file', __name__)

@download_file_bp.route('/scans/<int:scan_id>/download', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_file(scan_id):
    # Lade den Scan-Eintrag aus der Datenbank
    scan = db.session.query(Scan).get(scan_id)
    if not scan or not scan.filename:
        return jsonify({'error': 'Datei nicht gefunden'}), 404

    scan_dir = current_app.config.get('SCAN_FOLDER')
    current_app.logger.warning(f"Pfad: {scan_dir}")
    try:
        safe_join(scan_dir, scan.filename)
    except Exception:
        return jsonify({'error': 'Ungültiger Dateipfad'}), 400

    # Sende die Datei als Attachment
    return send_from_directory(
        scan_dir,           # <– directory
        scan.filename,              # <– path (Dateiname)
        as_attachment=True,
        download_name=scan.filename  # statt download_name
    )
    

@download_file_bp.route('/scans/<int:scan_id>/file/<path:filename>', methods=['GET', 'OPTIONS'])
@cross_origin()
def download_file_by_name(scan_id, filename):
    
    scan = db.session.query(Scan).get(scan_id)
    if not scan or not scan.filename:
        return jsonify({'error': 'Datei nicht gefunden'}), 404
    """
    Glaubt nur dem reinen Dateinamen (basename),
    sucht dann in SCAN_FOLDER danach und liefert es aus.
    """
    scan_dir = current_app.config.get('SCAN_FOLDER')
    if not scan_dir:
        current_app.logger.error("SCAN_FOLDER fehlt in der Konfiguration")
        return jsonify({'error': 'Server falsch konfiguriert'}), 500

    # Nur den Basename verwenden – so schummeln wir alle Verzeichnispfade weg
    fn = os.path.basename(filename)
    file_path = os.path.join(scan_dir, fn)
    print(file_path)
    current_app.logger.debug(f"Download versucht: {file_path}")

    if not os.path.isfile(file_path):
        current_app.logger.warning(f"Datei nicht gefunden: {file_path}")
        return jsonify({'error': 'Datei nicht gefunden'}), 404

    # direkt ausliefern
    return send_file(
        file_path,
        as_attachment=True,
        download_name=fn   # Flask ≥2.2; bei älteren Versionen: attachment_filename=fn
    )